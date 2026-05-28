# -*- coding: utf-8 -*-
"""
贞人占卜 — 商周龟甲灼兆卜辞应用
"""
import os
import sys

# 确保能找到模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.config import Config
# 竖屏锁定
Config.set("graphics", "width", "420")
Config.set("graphics", "height", "740")
Config.set("graphics", "resizable", False)
Config.set("kivy", "window_icon", "")

# ---------- 中文字体注册（必须在任何 Kivy UI 组件创建前执行）----------
from kivy.utils import platform
from kivy.core.text import LabelBase

if platform == "android":
    # Android — 尝试多个内建 CJK 字体路径
    for fnt in [
        "DroidSansFallback.ttf",
        "/system/fonts/DroidSansFallback.ttf",
        "/system/fonts/NotoSansCJK-Regular.ttc",
        "/system/fonts/NotoSansSC-Regular.otf",
    ]:
        if os.path.exists(fnt):
            LabelBase.register(name="Roboto", fn_regular=fnt)
            break
    else:
        LabelBase.register(name="Roboto", fn_regular="DroidSansFallback.ttf")
else:
    # Windows — 尝试多个系统中文字体
    for font_path in [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simkai.ttf",
    ]:
        if os.path.exists(font_path):
            LabelBase.register(name="Roboto", fn_regular=font_path)
            break

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from kivy.clock import Clock
from kivy.core.window import Window

from oracle_engine import OracleEngine


# ---------- 色彩常量 ----------
COLOR_BG = (0.07, 0.05, 0.02, 1)        # 深褐底色
COLOR_GOLD = (0.82, 0.63, 0.25, 1)      # 古铜金
COLOR_RED = (0.75, 0.18, 0.12, 1)       # 朱砂红
COLOR_CREAM = (0.93, 0.90, 0.82, 1)     # 骨白
COLOR_DARK = (0.12, 0.08, 0.04, 1)      # 深木色
COLOR_FIRE = (0.95, 0.42, 0.08, 1)      # 火焰橙


class HomeScreen(Screen):
    """首页 — 输入祈问事项"""

    def do_divination(self, question):
        question = question.strip()
        if not question:
            return
        app = App.get_running_app()
        app.current_question = question
        app.current_result = app.oracle.divine(question)
        self.manager.current = "ceremony"


class CeremonyScreen(Screen):
    """灼兆仪式 — 动画过渡屏"""

    def on_enter(self):
        # 3.5 秒后跳转到结果页
        Clock.schedule_once(self._go_result, 3.5)

    def on_leave(self):
        Clock.unschedule(self._go_result)

    def _go_result(self, dt):
        self.manager.current = "result"


class ResultScreen(Screen):
    """卜辞结果 — 展示 crack/oracle/explanation"""

    def on_pre_enter(self):
        app = App.get_running_app()
        r = app.current_result
        if r:
            self.ids.crack_label.text = r["crack_pattern"]
            self.ids.oracle_label.text = r["oracle_text"]
            self.ids.explain_label.text = r["explanation"]

    def go_home(self):
        self.manager.current = "home"

    def go_history(self):
        self.manager.current = "history"


class HistoryScreen(Screen):
    """历史记录 — 过往占卜列表"""

    def on_pre_enter(self):
        app = App.get_running_app()
        records = app.oracle.get_history()
        rv = self.ids.history_list
        rv.data = [
            {
                "question": rec[1],
                "oracle": rec[3],
                "time": rec[5],
                "record_id": str(rec[0]),
            }
            for rec in records
        ]

    def delete_record(self, record_id):
        app = App.get_running_app()
        app.oracle.delete_record(int(record_id))
        app.root.current = "history"


class ZhenRenApp(App):
    """贞人占卜 主应用"""

    title = "贞人占卜"

    def build(self):
        self.icon = ""
        Window.clearcolor = COLOR_BG
        self.oracle = OracleEngine()
        self.current_question = ""
        self.current_result = None
        sm = ScreenManager(transition=SlideTransition(duration=0.4))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(CeremonyScreen(name="ceremony"))
        sm.add_widget(ResultScreen(name="result"))
        sm.add_widget(HistoryScreen(name="history"))
        return sm

    def get_application_name(self):
        return "贞人占卜"


if __name__ == "__main__":
    ZhenRenApp().run()
