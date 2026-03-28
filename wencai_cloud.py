"""
问财股票监控 - 云端无头浏览器版 (GitHub Actions / Replit Ready)
功能：每 1 分钟自动访问问财，提取数据，保存为 CSV
环境：Ubuntu (GitHub Actions) / Linux (Replit)
依赖：selenium, webdriver-manager, pandas
"""
import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置
QUERY = "5日涨幅前50名，主板股，st股除外，股价低于40元，昨日阴线"
URL = f"https://search.10jqka.com.cn/html/wencaimobileresult/result.html?q={requests.utils.quote(QUERY)}&back_source=wxhy&share_hxapp=isc"
OUTPUT_FILE = "wencai_data.csv"
CHECK_INTERVAL = 60  # 秒

# Telegram 通知配置 (可选)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def send_telegram_message(message):
    """发送 Telegram 通知"""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        try:
            requests.post(url, json=data, timeout=10)
            logger.info("Telegram 通知发送成功")
        except Exception as e:
            logger.error(f"Telegram 通知失败: {e}")

def setup_driver():
    """配置无头浏览器 (云端优化)"""
    logger.info("正在配置浏览器...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 绕过检测
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # 在 GitHub Actions 中，ChromeDriver 已预装，无需 webdriver_manager
    if os.getenv("GITHUB_ACTIONS") == "true":
        logger.info("检测到 GitHub Actions 环境，使用系统预装 ChromeDriver")
        service = Service("/usr/bin/chromedriver")
    else:
        logger.info("尝试自动安装 ChromeDriver...")
        try:
            service = Service(ChromeDriverManager().install())
        except Exception as e:
            logger.error(f"ChromeDriver 安装失败: {e}")
            return None
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        logger.info("浏览器启动成功！")
        return driver
    except Exception as e:
        logger.error(f"浏览器启动失败: {e}")
        return None

def extract_data(driver):
    """提取表格数据"""
    try:
        logger.info("正在加载页面...")
        # 延长等待时间，确保 JS 渲染完成
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        tables = driver.find_elements(By.TAG_NAME, "table")
        if not tables:
            logger.warning("未找到表格元素")
            return []
        
        table = tables[0]
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        data = []
        headers = []
        
        for i, row in enumerate(rows):
            cells = row.find_elements(By.TAG_NAME, "td")
            if not cells:
                cells = row.find_elements(By.TAG_NAME, "th")
            if not cells:
                continue
            
            row_data = [cell.text.strip() for cell in cells]
            if i == 0:
                headers = row_data
            else:
                if any(row_data):
                    data.append(row_data)
        
        if headers and data:
            logger.info(f"成功解析 {len(data)} 行数据")
            return pd.DataFrame(data, columns=headers)
        else:
            logger.warning("表格为空或格式错误")
            return []
    except Exception as e:
        logger.error(f"解析失败: {e}")
        return []

def main():
    logger.info("="*60)
    logger.info("问财股票监控 - 云端版启动")
    logger.info(f"查询：{QUERY}")
    logger.info("="*60)
    
    driver = setup_driver()
    if not driver:
        send_telegram_message("❌ 浏览器启动失败，程序退出。")
        return
    
    try:
        iteration = 0
        while True:
            iteration += 1
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"\n[{now}] 第 {iteration} 次刷新...")
            
            try:
                driver.get(URL)
                logger.info("页面加载完成，正在提取数据...")
                
                df = extract_data(driver)
                
                if df.empty:
                    logger.warning("未提取到数据，等待下次刷新。")
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                logger.info(f"成功提取 {len(df)} 条数据。")
                
                # 保存数据
                df['采集时间'] = now
                file_exists = os.path.exists(OUTPUT_FILE)
                df.to_csv(OUTPUT_FILE, mode='a', header=(not file_exists), index=False, encoding='utf-8-sig')
                logger.info(f"数据已保存到 {OUTPUT_FILE}")
                
                # 发送 Telegram 通知 (前 5 只)
                if TELEGRAM_BOT_TOKEN:
                    msg = f"✅ 问财监控更新 ({now})\n共 {len(df)} 只股票\n\n前 5 只:\n"
                    for i, row in df.head(5).iterrows():
                        # 假设第一列是代码或名称
                        val = row.iloc[0] if len(row) > 0 else "N/A"
                        msg += f"{val}\n"
                    send_telegram_message(msg)
                
            except Exception as e:
                logger.error(f"本次刷新异常: {e}")
                send_telegram_message(f"⚠️ 监控异常: {str(e)[:100]}")
            
            logger.info(f"等待 {CHECK_INTERVAL} 秒...")
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("用户中断。")
    finally:
        driver.quit()
        logger.info("浏览器已关闭，程序结束。")

if __name__ == "__main__":
    main()
