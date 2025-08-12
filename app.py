import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import pytz

# 設定台灣時區
TW_TZ = pytz.timezone('Asia/Taipei')

def get_taiwan_time():
    """獲取台灣時間"""
    return datetime.now(TW_TZ)

# 頁面配置
st.set_page_config(
    page_title="🐉 天堂2M - 多群組BOSS追蹤器",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 群組配置
GROUPS = {
    "艾瑞卡1": {"icon": "⚔️", "color": "#e74c3c", "file_prefix": "erika1"},
    "艾瑞卡2": {"icon": "🛡️", "color": "#3498db", "file_prefix": "erika2"},
    "艾瑞卡3": {"icon": "🏹", "color": "#2ecc71", "file_prefix": "erika3"},
    "艾瑞卡4": {"icon": "🗡️", "color": "#f39c12", "file_prefix": "erika4"},
    "艾瑞卡5": {"icon": "🔮", "color": "#9b59b6", "file_prefix": "erika5"},
    "艾瑞卡6": {"icon": "⚡", "color": "#e67e22", "file_prefix": "erika6"},
    "黎歐納5": {"icon": "🌟", "color": "#16a085", "file_prefix": "leonard5"},
    "猛龍一盟": {"icon": "🐉", "color": "#c0392b", "file_prefix": "dragon1"},
    "猛龍二盟": {"icon": "🔥", "color": "#8e44ad", "file_prefix": "dragon2"},
}

# CSS 樣式
def get_group_css(group_name, group_config):
    return f"""
<style>
    .main-header-{group_config['file_prefix']} {{
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, {group_config['color']}, {group_config['color']}aa);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }}
    
    .boss-info-card-{group_config['file_prefix']} {{
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {group_config['color']};
        margin: 1rem 0;
    }}
    
    .click-hint-{group_config['file_prefix']} {{
        text-align: center;
        background-color: {group_config['color']}20;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border: 1px solid {group_config['color']}60;
    }}
    
    /* 手機版適配 */
    @media (max-width: 768px) {{
        .main-header-{group_config['file_prefix']} h1 {{
            font-size: 1.5rem !important;
        }}
        
        .stButton > button {{
            width: 100%;
            margin: 0.2rem 0;
        }}
        
        div[data-testid="stDataFrame"] {{
            font-size: 0.8rem;
        }}
        
        .stSelectbox > div > div {{
            font-size: 0.9rem;
        }}
    }}
    
    /* 隱藏Streamlit元素 */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* 表格行點擊效果 */
    .clickable-row {{
        cursor: pointer;
        transition: background-color 0.2s;
    }}
    
    .clickable-row:hover {{
        background-color: #f5f5f5 !important;
    }}
    
    /* 群組選擇器樣式 */
    .group-selector {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        color: white;
        text-align: center;
    }}
    
    .group-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        color: #333;
    }}
    
    .group-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }}
    
    /* 即將重生提醒樣式 */
    .upcoming-alert {{
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        animation: pulse 2s infinite;
    }}
    
    .upcoming-boss-item {{
        background: rgba(255, 255, 255, 0.1);
        margin: 0.5rem 0;
        padding: 0.75rem;
        border-radius: 8px;
        border-left: 4px solid #fff;
        backdrop-filter: blur(10px);
    }}
    
    @keyframes pulse {{
        0% {{ box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3); }}
        50% {{ box-shadow: 0 6px 25px rgba(255, 107, 107, 0.5); }}
        100% {{ box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3); }}
    }}
    
    .no-upcoming {{
        background: #f8f9fa;
        color: #6c757d;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        border: 2px dashed #dee2e6;
    }}
    
    /* 通知設定樣式 */
    .notification-settings {{
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #bbdefb;
    }}
    
    .notification-enabled {{
        background: #d5f4e6;
        border-color: #82c8a0;
    }}
    
    .notification-disabled {{
        background: #ffebee;
        border-color: #ffab91;
    }}
</style>
"""

class BossTracker:
    def __init__(self, group_prefix):
        self.data_file = f"{group_prefix}_boss_data.json"
        self.bosses = self.load_boss_data()
    
    def load_boss_data(self):
        """載入BOSS數據"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.get_default_bosses()
        else:
            return self.get_default_bosses()
    
    def get_default_bosses(self):
        """獲取默認BOSS列表"""
        return {
            "佩爾利斯": {"respawn_minutes": 120, "last_killed": None},
            "巴實那": {"respawn_minutes": 150, "last_killed": None},
            "采爾圖巴": {"respawn_minutes": 180, "last_killed": None},
            "潘納洛德": {"respawn_minutes": 180, "last_killed": None},
            "安庫拉": {"respawn_minutes": 210, "last_killed": None},
            "坦佛斯特": {"respawn_minutes": 210, "last_killed": None},
            "史坦": {"respawn_minutes": 240, "last_killed": None},
            "布賴卡": {"respawn_minutes": 240, "last_killed": None},
            "魔圖拉": {"respawn_minutes": 240, "last_killed": None},
            "特倫巴": {"respawn_minutes": 270, "last_killed": None},
            "提米特利斯": {"respawn_minutes": 300, "last_killed": None},
            "塔金": {"respawn_minutes": 300, "last_killed": None},
            "雷比魯": {"respawn_minutes": 300, "last_killed": None},
            "凱索思": {"respawn_minutes": 360, "last_killed": None},
            "巨蟻女王": {"respawn_minutes": 360, "last_killed": None},
            "卡雷斯": {"respawn_minutes": 360, "last_killed": None},
            "貝希莫斯": {"respawn_minutes": 360, "last_killed": None},
            "希瑟雷蒙": {"respawn_minutes": 360, "last_killed": None},
            "塔拉金": {"respawn_minutes": 420, "last_killed": None},
            "沙勒卡": {"respawn_minutes": 420, "last_killed": None},
            "梅杜莎": {"respawn_minutes": 420, "last_killed": None},
            "賽魯": {"respawn_minutes": 450, "last_killed": None},
            "潘柴特": {"respawn_minutes": 480, "last_killed": None},
            "突變克魯瑪": {"respawn_minutes": 480, "last_killed": None},
            "被汙染的克魯瑪": {"respawn_minutes": 480, "last_killed": None},
            "卡坦": {"respawn_minutes": 480, "last_killed": None},
            "提米妮爾": {"respawn_minutes": 480, "last_killed": None},
            "瓦柏": {"respawn_minutes": 480, "last_killed": None},
            "克拉奇": {"respawn_minutes": 480, "last_killed": None},
            "弗林特": {"respawn_minutes": 480, "last_killed": None},
            "蘭多勒": {"respawn_minutes": 480, "last_killed": None},
            "費德": {"respawn_minutes": 540, "last_killed": None},
            "寇倫": {"respawn_minutes": 600, "last_killed": None},
            "瑪杜克": {"respawn_minutes": 600, "last_killed": None},
            "薩班": {"respawn_minutes": 720, "last_killed": None},
            "核心基座": {"respawn_minutes": 720, "last_killed": None},
            "猛龍獸": {"respawn_minutes": 720, "last_killed": None},
            "黑色蕾爾莉": {"respawn_minutes": 720, "last_killed": None},
            "司穆艾爾": {"respawn_minutes": 720, "last_killed": None},
            "卡布里歐": {"respawn_minutes": 720, "last_killed": None},
            "安德拉斯": {"respawn_minutes": 720, "last_killed": None},
            "忘卻之鏡": {"respawn_minutes": 720, "last_killed": None},
            "納伊阿斯": {"respawn_minutes": 720, "last_killed": None},
            "希拉": {"respawn_minutes": 720, "last_killed": None},
            "姆夫": {"respawn_minutes": 720, "last_killed": None},
            "諾勒姆斯": {"respawn_minutes": 1080, "last_killed": None},
            "烏坎巴": {"respawn_minutes": 1080, "last_killed": None},
            "伊波斯": {"respawn_minutes": 1080, "last_killed": None},
            "凱都都": {"respawn_minutes": 1080, "last_killed": None},
            "伊格尼思": {"respawn_minutes": 1080, "last_killed": None},
            "奧爾芬": {"respawn_minutes": 1440, "last_killed": None},
            "哈普": {"respawn_minutes": 1440, "last_killed": None},
            "歐克斯": {"respawn_minutes": 1440, "last_killed": None},
            "塔那透斯": {"respawn_minutes": 1440, "last_killed": None},
            "鳳凰": {"respawn_minutes": 1440, "last_killed": None},
            "摩德烏斯": {"respawn_minutes": 1440, "last_killed": None},
            "霸拉克": {"respawn_minutes": 1440, "last_killed": None},
            "薩拉克斯": {"respawn_minutes": 1440, "last_killed": None},
            "巴倫": {"respawn_minutes": 1440, "last_killed": None},
            "黑卡頓": {"respawn_minutes": 1440, "last_killed": None},
            "拉何": {"respawn_minutes": 1980, "last_killed": None}
        }
    
    def save_boss_data(self):
        """保存BOSS數據"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.bosses, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"保存失敗: {e}")
            return False
    
    def calculate_respawn_info(self, boss_name, boss_data):
        """計算重生資訊"""
        if boss_data['last_killed'] is None:
            return "未擊殺", "等待擊殺", "⚪ 未記錄", "normal"
        
        try:
            last_killed = datetime.fromisoformat(boss_data['last_killed'])
            # 如果last_killed沒有時區資訊，假設它是台灣時間
            if last_killed.tzinfo is None:
                last_killed = TW_TZ.localize(last_killed)
            respawn_time = last_killed + timedelta(minutes=boss_data['respawn_minutes'])
            current_time = get_taiwan_time()
            
            last_killed_str = last_killed.strftime('%m/%d %H:%M:%S')
            respawn_time_str = respawn_time.strftime('%m/%d %H:%M:%S')
            
            if current_time >= respawn_time:
                return last_killed_str, respawn_time_str, "✅ 已重生", "ready"
            else:
                time_left = respawn_time - current_time
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                if hours > 0:
                    status = f"⏳ {hours}h{minutes}m"
                else:
                    status = f"⏳ {minutes}m"
                return last_killed_str, respawn_time_str, status, "waiting"
                
        except Exception as e:
            return "錯誤", "錯誤", "❌ 錯誤", "error"
    
    def get_boss_dataframe(self):
        """獲取BOSS數據框"""
        # 按重生時間排序
        sorted_bosses = sorted(self.bosses.items(), key=lambda x: x[1]['respawn_minutes'])
        
        data = []
        for index, (boss_name, boss_data) in enumerate(sorted_bosses, 1):
            respawn_minutes = boss_data['respawn_minutes']
            hours = respawn_minutes // 60
            minutes = respawn_minutes % 60
            
            if hours > 0:
                respawn_time_str = f"{hours}h{minutes}m" if minutes > 0 else f"{hours}h"
            else:
                respawn_time_str = f"{minutes}m"
            
            last_killed_str, respawn_time_str_full, status, status_type = self.calculate_respawn_info(boss_name, boss_data)
            
            data.append({
                '編號': f"{index:02d}",
                'BOSS名稱': boss_name,
                '重生時間': respawn_time_str,
                '上次擊殺': last_killed_str,
                '下次重生': respawn_time_str_full,
                '狀態': status,
                '_status_type': status_type  # 用於樣式
            })
        
        return pd.DataFrame(data)
    
    def get_upcoming_bosses(self, minutes_ahead=5):
        """獲取指定時間內即將重生的BOSS"""
        current_time = get_taiwan_time()
        upcoming_bosses = []
        
        for boss_name, boss_data in self.bosses.items():
            if boss_data['last_killed'] is None:
                continue
                
            try:
                last_killed = datetime.fromisoformat(boss_data['last_killed'])
                # 如果last_killed沒有時區資訊，假設它是台灣時間
                if last_killed.tzinfo is None:
                    last_killed = TW_TZ.localize(last_killed)
                
                respawn_time = last_killed + timedelta(minutes=boss_data['respawn_minutes'])
                time_until_respawn = respawn_time - current_time
                
                # 檢查是否在指定時間內重生
                if timedelta(0) <= time_until_respawn <= timedelta(minutes=minutes_ahead):
                    minutes_left = int(time_until_respawn.total_seconds() / 60)
                    seconds_left = int(time_until_respawn.total_seconds() % 60)
                    
                    upcoming_bosses.append({
                        'name': boss_name,
                        'respawn_time': respawn_time.strftime('%H:%M:%S'),
                        'time_left': f"{minutes_left}m{seconds_left}s" if minutes_left > 0 else f"{seconds_left}s",
                        'minutes_left': minutes_left,
                        'seconds_left': seconds_left
                    })
            except:
                continue
        
        # 按剩餘時間排序
        upcoming_bosses.sort(key=lambda x: x['minutes_left'] * 60 + x['seconds_left'])
        return upcoming_bosses
    
    def parse_time_string(self, time_str):
        """解析時間字串 - 僅支援兩種格式：MMDD/HHMMSS 和 HHMMSS"""
        try:
            time_str = time_str.strip()
            current_time = get_taiwan_time()
            
            # 格式1: MMDD/HHMMSS (例如: 0811/163045)
            if "/" in time_str and len(time_str) == 11:
                try:
                    date_part, time_part = time_str.split("/")
                    if len(date_part) == 4 and len(time_part) == 6:
                        month = int(date_part[:2])
                        day = int(date_part[2:])
                        hour = int(time_part[:2])
                        minute = int(time_part[2:4])
                        second = int(time_part[4:])
                        
                        # 使用當前年份並設定時區
                        year = current_time.year
                        parsed = datetime(year, month, day, hour, minute, second)
                        # 將解析的時間設定為台灣時區
                        parsed = TW_TZ.localize(parsed)
                        return parsed
                except (ValueError, IndexError):
                    pass
            
            # 格式2: HHMMSS (例如: 163045)
            elif len(time_str) == 6 and time_str.isdigit():
                try:
                    hour = int(time_str[:2])
                    minute = int(time_str[2:4])
                    second = int(time_str[4:])
                    
                    # 使用今天的日期並設定時區
                    today = current_time.date()
                    parsed = datetime.combine(today, datetime(1900, 1, 1, hour, minute, second).time())
                    # 將解析的時間設定為台灣時區
                    parsed = TW_TZ.localize(parsed)
                    return parsed
                except ValueError:
                    pass
            
            return None
        except Exception as e:
            print(f"時間解析錯誤: {e}")  # 調試用
            return None

# 初始化session state
if 'selected_group' not in st.session_state:
    st.session_state.selected_group = None

if 'boss_trackers' not in st.session_state:
    st.session_state.boss_trackers = {}

# 群組選擇頁面
def show_group_selector():
    st.markdown("""
    <div class="group-selector">
        <h1>🐉 天堂2M - 多群組BOSS追蹤器</h1>
        <p>📱 選擇您的群組開始追蹤BOSS重生時間</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 當前時間顯示
    current_time = get_taiwan_time().strftime('%Y/%m/%d %H:%M:%S')
    st.markdown(f"<div style='text-align: center; margin: 2rem 0; font-size: 1.2rem;'>⏰ 現在時間: {current_time}</div>", unsafe_allow_html=True)
    
    st.markdown("### 🎯 選擇您的群組")
    
    # 使用4列佈局顯示群組
    cols = st.columns(4)
    
    for i, (group_name, group_config) in enumerate(GROUPS.items()):
        col_idx = i % 4
        
        with cols[col_idx]:
            if st.button(
                f"{group_config['icon']} {group_name}",
                key=f"group_btn_{group_config['file_prefix']}",
                use_container_width=True
            ):
                st.session_state.selected_group = group_name
                # 初始化對應的tracker
                if group_name not in st.session_state.boss_trackers:
                    st.session_state.boss_trackers[group_name] = BossTracker(group_config['file_prefix'])
                st.rerun()

# BOSS追蹤頁面
def show_boss_tracker(group_name, group_config):
    # 載入群組專屬CSS
    st.markdown(get_group_css(group_name, group_config), unsafe_allow_html=True)
    
    # 側邊欄 - 群組切換
    with st.sidebar:
        st.markdown(f"### {group_config['icon']} 當前群組")
        st.markdown(f"**{group_name}**")
        
        if st.button("🔄 切換群組", use_container_width=True):
            st.session_state.selected_group = None
            st.rerun()
        
    
    # 獲取對應的tracker
    tracker = st.session_state.boss_trackers[group_name]
    
    # 主標題
    st.markdown(f"""
    <div class="main-header-{group_config['file_prefix']}">
        <h1>{group_config['icon']} {group_name} - BOSS重生追蹤器</h1>
        <p>📱 群組專用數據 | 台灣時區 | 即時同步</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 當前時間顯示
    current_time = get_taiwan_time().strftime('%Y/%m/%d %H:%M:%S')
    st.markdown(f"<div style='text-align: center; margin: 1rem 0; font-size: 1.1rem;'>⏰ 現在時間: {current_time}</div>", unsafe_allow_html=True)
    
    # 獲取BOSS數據
    df = tracker.get_boss_dataframe()
    
    # 統計信息
    total_bosses = len(df)
    ready_bosses = len(df[df['狀態'].str.contains('✅')])
    waiting_bosses = len(df[df['狀態'].str.contains('⏳')])
    
    # 響應式佈局
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        st.metric("總BOSS數", total_bosses)
    
    with col2:
        st.metric("已重生", ready_bosses)
    
    with col3:
        st.metric("等待中", waiting_bosses)
    
    with col4:
        st.metric("未記錄", total_bosses - ready_bosses - waiting_bosses)
    
    # 桌面通知設定
    st.markdown("### 🔔 桌面通知設定")
    
    # 通知測試按鈕
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧪 測試通知功能", help="發送一個測試通知確認功能正常"):
            test_notification_js = """
            <script>
            (function() {
                console.log('=== 測試通知功能 ===');
                console.log('瀏覽器支援通知:', 'Notification' in window);
                
                if (!('Notification' in window)) {
                    alert('您的瀏覽器不支援桌面通知功能！');
                    return;
                }
                
                const currentPermission = Notification.permission;
                console.log('當前通知權限:', currentPermission);
                
                if (currentPermission === 'granted') {
                    console.log('發送測試通知');
                    try {
                        const notification = new Notification('🧪 測試通知', {
                            body: '如果您看到這個通知，表示功能正常運作！',
                            icon: 'data:image/svg+xml;base64,' + btoa('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">✅</text></svg>'),
                            requireInteraction: true,
                            tag: 'test-notification'
                        });
                        
                        notification.onclick = function() {
                            window.focus();
                            notification.close();
                        };
                        
                        setTimeout(() => notification.close(), 5000);
                        console.log('測試通知已發送');
                    } catch (error) {
                        console.error('發送通知時發生錯誤:', error);
                        alert('發送通知失敗: ' + error.message);
                    }
                } else if (currentPermission === 'denied') {
                    alert('桌面通知權限已被拒絕！\\n請到瀏覽器設定中允許通知，或點擊網址列左側的通知圖示。');
                } else {
                    alert('請先點擊「🔔 啟用桌面通知」按鈕來授予權限！');
                }
            })();
            </script>
            """
            st.markdown(test_notification_js, unsafe_allow_html=True)
    
    with col2:
        if st.button("🔍 檢查Debug日誌", help="在瀏覽器控制台查看詳細日誌"):
            debug_js = """
            <script>
            (function() {
                console.log('=== 通知功能診斷 ===');
                console.log('瀏覽器支援通知:', 'Notification' in window);
                console.log('當前權限狀態:', Notification.permission);
                console.log('即將重生項目數量:', document.querySelectorAll('.upcoming-boss-item').length);
                
                // 列出所有即將重生的BOSS項目
                const items = document.querySelectorAll('.upcoming-boss-item');
                console.log('找到的BOSS項目:');
                items.forEach((item, index) => {
                    console.log(`${index + 1}. ${item.textContent}`);
                });
                
                // 檢查通知相關函數是否存在
                console.log('checkUpcomingBosses函數存在:', typeof checkUpcomingBosses !== 'undefined');
                console.log('sendNotification函數存在:', typeof sendNotification !== 'undefined');
                
                // 嘗試手動觸發檢查
                if (typeof checkUpcomingBosses !== 'undefined') {
                    console.log('手動觸發BOSS檢查...');
                    try {
                        checkUpcomingBosses();
                    } catch (error) {
                        console.error('檢查BOSS時發生錯誤:', error);
                    }
                } else {
                    console.warn('checkUpcomingBosses函數未定義');
                }
                
                alert('Debug資訊已輸出到控制台！\\n請按F12開啟開發者工具查看Console日誌。');
            })();
            </script>
            """
            st.markdown(debug_js, unsafe_allow_html=True)
    
    # JavaScript for notifications
    notification_js = """
    <script>
    let notificationPermission = 'default';
    let notifiedBosses = new Set();
    
    // 檢查通知權限
    function checkNotificationPermission() {
        if ('Notification' in window) {
            notificationPermission = Notification.permission;
            updateNotificationStatus();
        }
    }
    
    // 請求通知權限
    function requestNotificationPermission() {
        if ('Notification' in window) {
            Notification.requestPermission().then(function(permission) {
                notificationPermission = permission;
                updateNotificationStatus();
            });
        }
    }
    
    // 更新通知狀態顯示
    function updateNotificationStatus() {
        const statusDiv = document.getElementById('notification-status');
        if (statusDiv) {
            if (notificationPermission === 'granted') {
                statusDiv.innerHTML = '<div class="notification-settings notification-enabled">✅ 桌面通知已啟用</div>';
            } else if (notificationPermission === 'denied') {
                statusDiv.innerHTML = '<div class="notification-settings notification-disabled">❌ 桌面通知已被拒絕<br><small>請在瀏覽器設定中允許通知</small></div>';
            } else {
                statusDiv.innerHTML = '<div class="notification-settings"><button onclick="requestNotificationPermission()" style="background: #2196F3; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">🔔 啟用桌面通知</button></div>';
            }
        }
    }
    
    // 發送通知
    function sendNotification(title, body, icon = '🐉') {
        if (notificationPermission === 'granted') {
            const notification = new Notification(title, {
                body: body,
                icon: 'data:image/svg+xml;base64,' + btoa('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">' + icon + '</text></svg>'),
                requireInteraction: true,
                tag: 'boss-notification'
            });
            
            notification.onclick = function() {
                window.focus();
                notification.close();
            };
            
            // 5秒後自動關閉
            setTimeout(() => notification.close(), 5000);
        }
    }
    
    // 檢查即將重生的BOSS並發送通知
    function checkUpcomingBosses() {
        try {
            console.log('=== 開始檢查即將重生的BOSS ===');
            const upcomingItems = document.querySelectorAll('.upcoming-boss-item');
            console.log(`找到 ${upcomingItems.length} 個即將重生的BOSS項目`);
            
            if (upcomingItems.length === 0) {
                console.log('沒有即將重生的BOSS，結束檢查');
                return;  // 沒有即將重生的BOSS
            }
            
            upcomingItems.forEach((item, index) => {
                try {
                    console.log(`檢查第 ${index + 1} 個BOSS項目`);
                    const strongElement = item.querySelector('strong');
                    if (!strongElement) {
                        console.log('找不到strong元素，跳過');
                        return;
                    }
                    
                    const bossName = strongElement.textContent.replace('🎯 ', '').trim();
                    const timeText = item.textContent;
                    console.log(`BOSS名稱: ${bossName}`);
                    console.log(`時間文字: ${timeText}`);
                    
                    // 提取重生時間和剩餘時間
                    const respawnTimeMatch = timeText.match(/重生時間:\\s*([^|]+)/);
                    // 修正正則表達式以匹配實際格式
                    const timeMatch = timeText.match(/剩餘:\\s*<strong>(\\d+)m(\\d+)s<\\/strong>|剩餘:\\s*<strong>(\\d+)s<\\/strong>|剩餘:\\s*(\\d+)m(\\d+)s|剩餘:\\s*(\\d+)s/);
                    
                    console.log(`重生時間匹配: ${respawnTimeMatch}`);
                    console.log(`剩餘時間匹配: ${timeMatch}`);
                    
                    let respawnTime = '未知時間';
                    if (respawnTimeMatch) {
                        respawnTime = respawnTimeMatch[1].trim();
                        console.log(`解析的重生時間: ${respawnTime}`);
                    }
                    
                    if (timeMatch) {
                        let totalSeconds = 0;
                        if (timeMatch[1] && timeMatch[2]) {
                            // 格式: <strong>XmYs</strong>
                            totalSeconds = parseInt(timeMatch[1]) * 60 + parseInt(timeMatch[2]);
                        } else if (timeMatch[3]) {
                            // 格式: <strong>Xs</strong>
                            totalSeconds = parseInt(timeMatch[3]);
                        } else if (timeMatch[4] && timeMatch[5]) {
                            // 格式: XmYs (無<strong>標籤)
                            totalSeconds = parseInt(timeMatch[4]) * 60 + parseInt(timeMatch[5]);
                        } else if (timeMatch[6]) {
                            // 格式: Xs (無<strong>標籤)
                            totalSeconds = parseInt(timeMatch[6]);
                        }
                        
                        console.log(`解析的總秒數: ${totalSeconds}`);
                        
                        // 5分鐘內重生提醒
                        if (totalSeconds <= 300 && totalSeconds > 0) {
                            const notificationKey = bossName + '_5min';
                            if (!notifiedBosses.has(notificationKey)) {
                                sendNotification(
                                    '🚨 BOSS即將重生！',
                                    `${bossName}\\n下次重生時間: ${respawnTime}\\n將在${Math.floor(totalSeconds/60)}分${totalSeconds%60}秒內重生，快去準備！`,
                                    '⚔️'
                                );
                                notifiedBosses.add(notificationKey);
                                console.log(`發送5分鐘提醒: ${bossName} - ${respawnTime}`);
                            }
                        }
                        
                        // 已重生提醒
                        if (totalSeconds <= 0) {
                            const notificationKey = bossName + '_respawned';
                            if (!notifiedBosses.has(notificationKey)) {
                                sendNotification(
                                    '✅ BOSS已重生！',
                                    `${bossName}\\n重生時間: ${respawnTime}\\n現在可以挑戰了！`,
                                    '🎯'
                                );
                                notifiedBosses.add(notificationKey);
                                console.log(`發送重生提醒: ${bossName} - ${respawnTime}`);
                            }
                        }
                    }
                    
                    // 檢查是否顯示"已重生"文字（備用檢查）
                    if (timeText.includes('已重生') || timeText.includes('可挑戰')) {
                        const notificationKey = bossName + '_respawned';
                        if (!notifiedBosses.has(notificationKey)) {
                            // 提取重生時間
                            const respawnTimeMatch = timeText.match(/重生時間:\\s*([^|]+)/);
                            let respawnTime = '未知時間';
                            if (respawnTimeMatch) {
                                respawnTime = respawnTimeMatch[1].trim();
                            }
                            
                            sendNotification(
                                '✅ BOSS已重生！',
                                `${bossName}\\n重生時間: ${respawnTime}\\n現在可以挑戰了！`,
                                '🎯'
                            );
                            notifiedBosses.add(notificationKey);
                            console.log(`發送重生提醒(文字): ${bossName} - ${respawnTime}`);
                        }
                    }
                } catch (e) {
                    console.error('處理單個BOSS通知時出錯:', e);
                }
            });
        } catch (error) {
            console.error('檢查即將重生BOSS時出錯:', error);
        }
    }
    
    // 頁面載入時檢查權限
    document.addEventListener('DOMContentLoaded', function() {
        checkNotificationPermission();
        
        // 每10秒檢查一次即將重生的BOSS
        setInterval(checkUpcomingBosses, 10000);
        
        // 3秒後進行首次檢查
        setTimeout(checkUpcomingBosses, 3000);
    });
    
    // Streamlit重新運行時也檢查權限和狀態
    setTimeout(() => {
        checkNotificationPermission();
        updateNotificationStatus();
    }, 1000);
    
    // 頁面加載時立即初始化
    document.addEventListener('DOMContentLoaded', function() {
        checkNotificationPermission();
        updateNotificationStatus();
    });
    
    // 確保狀態更新
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            checkNotificationPermission();
            updateNotificationStatus();
        });
    } else {
        setTimeout(() => {
            checkNotificationPermission();
            updateNotificationStatus();
        }, 500);
    }
    </script>
    
    <div id="notification-status"></div>
    """
    
    st.markdown(notification_js, unsafe_allow_html=True)
    
    # 即將重生提醒
    upcoming_bosses = tracker.get_upcoming_bosses(5)  # 5分鐘內即將重生
    
    if upcoming_bosses:
        st.markdown("### 🚨 即將重生提醒 (5分鐘內)")
        
        for boss in upcoming_bosses:
            st.write(f"🎯 **{boss['name']}** - 下次重生時間: {boss['respawn_time']}")
        
        # 添加JavaScript來觸發通知檢查（使用JavaScript動態創建隱藏元素）
        upcoming_js_data = []
        for boss in upcoming_bosses:
            upcoming_js_data.append({
                'name': boss['name'],
                'respawn_time': boss['respawn_time'],
                'time_left': boss['time_left']
            })
        
        st.markdown(f"""
        <script>
        // 動態創建隱藏的BOSS項目供通知檢查使用
        function createHiddenBossItems() {{
            const bossData = {upcoming_js_data};
            const container = document.createElement('div');
            container.style.display = 'none';
            container.id = 'hidden-boss-container';
            
            // 移除舊的容器
            const oldContainer = document.getElementById('hidden-boss-container');
            if (oldContainer) {{
                oldContainer.remove();
            }}
            
            bossData.forEach(boss => {{
                const item = document.createElement('div');
                item.className = 'upcoming-boss-item';
                item.innerHTML = `
                    <strong>🎯 ${{boss.name}}</strong>
                    <br>
                    重生時間: ${{boss.respawn_time}} | 剩餘: <strong>${{boss.time_left}}</strong>
                `;
                container.appendChild(item);
            }});
            
            document.body.appendChild(container);
        }}
        
        // 創建隱藏元素並開始檢查
        createHiddenBossItems();
        setTimeout(checkUpcomingBosses, 2000);
        setInterval(checkUpcomingBosses, 30000); // 每30秒檢查一次
        </script>
        """, unsafe_allow_html=True)
        
    else:
        st.markdown("### 📅 即將重生提醒")
        st.markdown("""
        <div class="no-upcoming">
            <p>😴 目前沒有BOSS在5分鐘內重生</p>
            <small>繼續狩獵吧！系統會自動提醒您</small>
        </div>
        """, unsafe_allow_html=True)
    
    # BOSS表格顯示
    st.markdown("### 📊 BOSS狀態一覽")
    
    # 使用原生顏色樣式，不額外設定避免衝突
    display_df = df.drop('_status_type', axis=1)
    
    # 可點擊的表格，支援選取行來更新擊殺時間
    selected_rows = st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        selection_mode="single-row",
        on_select="rerun",
        column_config={
            "編號": st.column_config.TextColumn("編號", width="small"),
            "BOSS名稱": st.column_config.TextColumn("BOSS名稱", width="medium"), 
            "重生時間": st.column_config.TextColumn("重生時間", width="small"),
            "上次擊殺": st.column_config.TextColumn("上次擊殺", width="medium"),
            "下次重生": st.column_config.TextColumn("下次重生", width="medium"),
            "狀態": st.column_config.TextColumn("狀態", width="medium")
        }
    )
    
    # 處理表格點擊選取
    if selected_rows.selection.rows:
        selected_row_idx = selected_rows.selection.rows[0]
        selected_boss_name = display_df.iloc[selected_row_idx]['BOSS名稱']
        
        # 顯示快速更新按鈕
        st.markdown(f"### 🎯 快速更新：{selected_boss_name}")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**選中BOSS**: {selected_boss_name}")
            current_record = "無記錄"
            if tracker.bosses[selected_boss_name]['last_killed']:
                try:
                    dt = datetime.fromisoformat(tracker.bosses[selected_boss_name]['last_killed'])
                    # 如果沒有時區資訊，假設是台灣時間
                    if dt.tzinfo is None:
                        dt = TW_TZ.localize(dt)
                    current_record = dt.strftime('%Y/%m/%d %H:%M:%S')
                except:
                    current_record = "格式錯誤"
            st.markdown(f"**當前記錄**: {current_record}")
        
        with col2:
            if st.button("⚡ 更新為現在時間", use_container_width=True, type="primary", key="quick_update"):
                tracker.bosses[selected_boss_name]['last_killed'] = get_taiwan_time().isoformat()
                if tracker.save_boss_data():
                    st.success(f"✅ 已更新 {selected_boss_name} 擊殺時間")
                    st.rerun()
        
        with col3:
            if st.button("🗑️ 清除記錄", use_container_width=True, key="quick_clear"):
                tracker.bosses[selected_boss_name]['last_killed'] = None
                if tracker.save_boss_data():
                    st.success(f"✅ 已清除 {selected_boss_name} 記錄")
                    st.rerun()
        
        st.markdown("---")
    
    # 點擊提示
    st.markdown(f"""
    <div class="click-hint-{group_config['file_prefix']}">
        💡 <strong>操作說明</strong>：點擊表格中的任一行選擇BOSS，然後使用快速更新按鈕，或使用下方手動輸入區域
    </div>
    """, unsafe_allow_html=True)
    
    # 分隔線
    st.markdown("---")
    
    # 手動更新區域
    st.markdown("### 📝 更新BOSS擊殺時間")
    
    # 響應式佈局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # BOSS選擇
        boss_names = list(tracker.bosses.keys())
        
        # 根據重生時間排序BOSS名稱顯示
        sorted_boss_items = sorted(tracker.bosses.items(), key=lambda x: x[1]['respawn_minutes'])
        sorted_boss_names = [name for name, _ in sorted_boss_items]
        
        selected_boss = st.selectbox(
            "🎯 選擇要更新的BOSS",
            sorted_boss_names,
            index=0,
            key="boss_selector"
        )
        
        # 顯示選中BOSS信息
        if selected_boss:
            boss_data = tracker.bosses[selected_boss]
            current_record = "無記錄"
            if boss_data['last_killed']:
                try:
                    dt = datetime.fromisoformat(boss_data['last_killed'])
                    # 如果沒有時區資訊，假設是台灣時間
                    if dt.tzinfo is None:
                        dt = TW_TZ.localize(dt)
                    current_record = dt.strftime('%Y/%m/%d %H:%M:%S')
                except:
                    current_record = "格式錯誤"
            
            respawn_minutes = boss_data['respawn_minutes']
            hours = respawn_minutes // 60
            minutes = respawn_minutes % 60
            respawn_str = f"{hours}h{minutes}m" if minutes > 0 else f"{hours}h" if hours > 0 else f"{minutes}m"
            
            st.markdown(f"""
            <div class="boss-info-card-{group_config['file_prefix']}">
                <strong>🎯 {selected_boss}</strong><br>
                <small>重生時間: {respawn_str} | 當前記錄: {current_record}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # 快速操作按鈕
        st.markdown("#### ⚡ 快速操作")
        
        if st.button("🕐 記錄現在時間", use_container_width=True, type="primary"):
            if selected_boss:
                tracker.bosses[selected_boss]['last_killed'] = get_taiwan_time().isoformat()
                if tracker.save_boss_data():
                    st.success(f"✅ 已記錄 {selected_boss} 擊殺於 {get_taiwan_time().strftime('%H:%M:%S')}")
                    st.rerun()
        
        if st.button("🗑️ 清除此BOSS記錄", use_container_width=True):
            if selected_boss:
                tracker.bosses[selected_boss]['last_killed'] = None
                if tracker.save_boss_data():
                    st.success(f"✅ 已清除 {selected_boss} 的記錄")
                    st.rerun()
    
    # 手動輸入時間
    st.markdown("#### ⏰ 手動輸入擊殺時間")
    
    # 顯示支援的時間格式
    st.markdown("""
    <div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
        <strong>📋 支援的時間格式：</strong><br>
        • <code>0811/163045</code> - 月日/時分秒 (8月11日 16:30:45)<br>
        • <code>163045</code> - 時分秒 (今天 16:30:45)<br>
        <small style="color: #666;">注意：所有數字必須是兩位數，例如 08 而非 8</small>
    </div>
    """, unsafe_allow_html=True)
    
    # 檢查是否需要清空輸入框
    clear_key = f"clear_input_{group_config['file_prefix']}"
    input_key = f"time_input_{group_config['file_prefix']}"
    
    # 如果有清空標記，設定空值並移除標記
    if st.session_state.get(clear_key, False):
        if input_key in st.session_state:
            del st.session_state[input_key]
        del st.session_state[clear_key]
        # 使用 rerun 重新渲染頁面
        st.rerun()
    
    time_input = st.text_input(
        "擊殺時間",
        placeholder="例如: 163045 或 0811/163045",
        help="輸入格式：時分秒(HHMMSS) 或 月日/時分秒(MMDD/HHMMSS)",
        key=input_key
    )
    
    # 更新按鈕
    if st.button("🎯 更新擊殺時間", use_container_width=True, type="secondary"):
        # 優先使用表格選擇的BOSS，如果沒有則使用下拉選單選擇的BOSS
        target_boss = None
        if selected_rows.selection.rows:
            selected_row_idx = selected_rows.selection.rows[0]
            target_boss = display_df.iloc[selected_row_idx]['BOSS名稱']
        elif selected_boss:
            target_boss = selected_boss
        
        if not target_boss:
            st.error("⚠️ 請先點擊表格中的任一行選擇BOSS，或使用下拉選單選擇")
        elif not time_input.strip():
            # 清除記錄
            tracker.bosses[target_boss]['last_killed'] = None
            if tracker.save_boss_data():
                st.success(f"✅ 已清除 {target_boss} 的擊殺記錄")
                st.rerun()
        else:
            # 解析時間
            parsed_time = tracker.parse_time_string(time_input)
            if parsed_time is None:
                st.error(f"""
                ⚠️ **時間格式不正確！**
                
                請使用以下格式之一：
                - `0811/163045` (月日/時分秒)
                - `163045` (時分秒，使用今天)
                
                **注意**：所有數字必須是兩位數
                
                **您輸入的**: `{time_input}`
                """)
            else:
                # 檢查時間是否合理（不能是太久以前或未來）
                current_time = get_taiwan_time()
                time_diff = current_time - parsed_time
                
                # 檢查時間合理性，但不阻止更新
                if time_diff.total_seconds() < 0:
                    st.warning("⚠️ 您輸入的時間是未來時間")
                elif time_diff.total_seconds() > 86400 * 7:  # 超過7天
                    st.warning("⚠️ 您輸入的時間是7天前")
                
                # 執行更新
                try:
                    tracker.bosses[target_boss]['last_killed'] = parsed_time.isoformat()
                    if tracker.save_boss_data():
                        respawn_time = parsed_time + timedelta(minutes=tracker.bosses[target_boss]['respawn_minutes'])
                        time_until_respawn = respawn_time - current_time
                        
                        if time_until_respawn.total_seconds() > 0:
                            hours = int(time_until_respawn.total_seconds() // 3600)
                            minutes = int((time_until_respawn.total_seconds() % 3600) // 60)
                            st.success(f"""
                            ✅ **更新成功！**
                            
                            **BOSS**: {target_boss}  
                            **擊殺時間**: {parsed_time.strftime('%Y/%m/%d %H:%M:%S')}  
                            **重生時間**: {respawn_time.strftime('%Y/%m/%d %H:%M:%S')}  
                            **剩餘時間**: {hours}小時{minutes}分鐘
                            """)
                        else:
                            st.success(f"""
                            ✅ **更新成功！**
                            
                            **BOSS**: {target_boss}  
                            **擊殺時間**: {parsed_time.strftime('%Y/%m/%d %H:%M:%S')}  
                            **狀態**: 🎯 已可重生！
                            """)
                        
                        # 設定清空標記，在下次rerun時清空輸入框
                        st.session_state[f"clear_input_{group_config['file_prefix']}"] = True
                        
                        # 重新運行頁面
                        st.rerun()
                    else:
                        st.error("❌ 儲存失敗，請重試")
                except Exception as e:
                    st.error(f"❌ 更新失敗: {e}")
    
    # 分隔線
    st.markdown("---")
    
    # 批量操作
    st.markdown("### 🛠️ 系統功能")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 重新載入數據", use_container_width=True):
            st.session_state.boss_trackers[group_name] = BossTracker(group_config['file_prefix'])
            st.success("✅ 數據已重新載入")
            st.rerun()
    
    with col2:
        if st.button("🗑️ 清除所有記錄", use_container_width=True, type="secondary"):
            # 二次確認
            if st.session_state.get(f'confirm_clear_all_{group_config["file_prefix"]}', False):
                for boss_name in tracker.bosses:
                    tracker.bosses[boss_name]['last_killed'] = None
                if tracker.save_boss_data():
                    st.success("✅ 已清除所有BOSS記錄")
                    st.session_state[f'confirm_clear_all_{group_config["file_prefix"]}'] = False
                    st.rerun()
            else:
                st.session_state[f'confirm_clear_all_{group_config["file_prefix"]}'] = True
                st.warning("⚠️ 請再次點擊確認清除所有記錄")
    
    with col3:
        # 下載數據備份
        backup_data = json.dumps(tracker.bosses, ensure_ascii=False, indent=2)
        st.download_button(
            "💾 下載備份",
            backup_data,
            file_name=f"{group_config['file_prefix']}_backup_{get_taiwan_time().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    # 底部信息
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #666; margin: 2rem 0;'>
        <p>{group_config['icon']} {group_name} - BOSS重生追蹤器</p>
        <p>📱 支援手機、平板、電腦 | 🌐 群組專用數據 | ⏰ 台灣時區</p>
        <small>✅ 點擊表格更新 ✅ 精確到秒 ✅ 即時同步</small>
    </div>
    """, unsafe_allow_html=True)

# 主程式邏輯
if st.session_state.selected_group is None:
    show_group_selector()
else:
    group_name = st.session_state.selected_group
    group_config = GROUPS[group_name]
    show_boss_tracker(group_name, group_config)