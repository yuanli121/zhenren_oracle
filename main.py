# -*- coding: utf-8 -*-
"""
爻一摇 — 商周龟甲灼兆卜辞应用
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


class SplashScreen(Screen):
    """开机动画 — 大文件自动跳过，避免卡死"""

    def on_enter(self):
        Clock.schedule_once(self._start_splash, 0.5)

    def _start_splash(self, dt):
        video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "splash_anim.mp4")
        try:
            size_mb = os.path.getsize(video_path) / (1024 * 1024)
        except Exception:
            self._skip()
            return
        # 大于 50MB 直接跳过
        if size_mb > 50:
            self._skip()
            return
        from kivy.uix.video import Video as V
        video = None
        for child in self.children:
            if isinstance(child, V):
                video = child
                break
        if video is None:
            self._skip()
            return
        try:
            video.source = video_path
            video.state = "play"
            video.bind(eos=self._on_video_end)
        except Exception:
            self._skip()
            return
        # 4 秒超时兜底
        Clock.schedule_once(self._go_home, 4)

    def _on_video_end(self, instance, value):
        if value:
            Clock.unschedule(self._go_home)
            self.manager.current = "home"

    def _go_home(self, dt):
        if self.manager.current == "splash":
            self.manager.current = "home"

    def _skip(self):
        self.manager.current = "home"

    def on_leave(self):
        Clock.unschedule(self._go_home)
        from kivy.uix.video import Video as V
        for child in self.children:
            if isinstance(child, V):
                child.unbind(eos=self._on_video_end)
                child.state = "stop"
                break


class HomeScreen(Screen):
    """首页 — 输入祈问事项"""

    def do_divination(self, question):
        question = question.strip()
        if not question:
            return
        app = App.get_running_app()
        # 检查免费次数 / 激活状态
        if not app.oracle.is_activated() and app.oracle.get_free_uses_left() <= 0:
            self.manager.current = "paywall"
            return
        app.current_question = question
        app.current_result = app.oracle.divine(question)
        app.oracle.increment_usage()
        self.manager.current = "ceremony"


class CeremonyScreen(Screen):
    """灼兆仪式 — 视频动画，完整播放，短超时兜底"""

    def on_enter(self):
        Clock.schedule_once(self._start_ceremony, 0.5)

    def _start_ceremony(self, dt):
        from kivy.uix.video import Video as V
        video = None
        for child in self.children:
            if isinstance(child, V):
                video = child
                break
        if video is None:
            Clock.schedule_once(self._go_result, 2)
            return
        video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "divination_anim.mp4")
        if not os.path.exists(video_path):
            Clock.schedule_once(self._go_result, 2)
            return
        try:
            video.source = video_path
            video.state = "play"
            video.bind(eos=self._on_video_end)
        except Exception:
            Clock.schedule_once(self._go_result, 2)
            return
        # 5 秒超时兜底（视频应在这之前结束）
        Clock.schedule_once(self._go_result, 5)

    def _on_video_end(self, instance, value):
        if value:
            Clock.unschedule(self._go_result)
            self.manager.current = "result"

    def on_leave(self):
        Clock.unschedule(self._go_result)
        from kivy.uix.video import Video as V
        for child in self.children:
            if isinstance(child, V):
                child.unbind(eos=self._on_video_end)
                child.state = "stop"
                break

    def _go_result(self, dt):
        if self.manager.current == "ceremony":
            self.manager.current = "result"


class PaywallScreen(Screen):
    """付费解锁 — 试用次数用完"""

    def on_pre_enter(self):
        app = App.get_running_app()
        left = app.oracle.get_free_uses_left()
        activated = app.oracle.is_activated()
        self.ids.paywall_status.text = (
            "已激活 · 无限使用" if activated else f"免费试用：剩余 {left} 次"
        )

    def try_activate(self, code):
        app = App.get_running_app()
        if app.oracle.verify_code(code):
            self.ids.paywall_msg.text = "激活成功！\n感谢支持，现在可以无限占卜了。"
            self.ids.paywall_msg.color = (0.84, 0.67, 0.30, 1)
            self.ids.paywall_status.text = "已激活 · 无限使用"
        else:
            self.ids.paywall_msg.text = "激活码无效，请检查后重试。\n如需购买请联系开发者。"
            self.ids.paywall_msg.color = (0.75, 0.18, 0.12, 1)

    def go_home(self):
        self.manager.current = "home"


class ResultScreen(Screen):
    """卜辞结果 — 展示 crack/oracle/explanation"""

    def on_pre_enter(self):
        app = App.get_running_app()
        r = app.current_result
        if r:
            self.ids.crack_label.text = r["crack_pattern"]
            self.ids.oracle_label.text = r["oracle_text"]
            self.ids.explain_label.text = r["explanation"]
            self.ids.auspice_label.text = r.get("auspice_label", "无咎 · 安常")
            # 吉凶配色
            auspice = r.get("auspice", "无咎")
            auspice_colors = {
                "大吉": (0.95, 0.55, 0.10, 1),
                "吉": (0.84, 0.67, 0.30, 1),
                "贞吉": (0.72, 0.60, 0.32, 1),
                "无咎": (0.60, 0.52, 0.38, 1),
                "悔吝": (0.55, 0.45, 0.32, 1),
                "厉": (0.75, 0.18, 0.12, 1),
            }
            self.ids.auspice_label.color = auspice_colors.get(auspice, (0.6, 0.52, 0.38, 1))

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
                "time": rec[6],
                "auspice": rec[5],
                "record_id": str(rec[0]),
            }
            for rec in records
        ]

    def delete_record(self, record_id):
        app = App.get_running_app()
        app.oracle.delete_record(int(record_id))
        app.root.current = "history"


class YaoYiYaoApp(App):
    """爻一摇 主应用"""

    title = "爻一摇"

    def build(self):
        self.icon = ""
        Window.clearcolor = COLOR_BG
        self.oracle = OracleEngine()
        self.current_question = ""
        self.current_result = None
        sm = ScreenManager(transition=SlideTransition(duration=0.4))
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(CeremonyScreen(name="ceremony"))
        sm.add_widget(ResultScreen(name="result"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(PaywallScreen(name="paywall"))
        return sm

    def get_application_name(self):
        return "爻一摇"


if __name__ == "__main__":
    YaoYiYaoApp().run()
