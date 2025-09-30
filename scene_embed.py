from __future__ import annotations

import inspect
import pyperclip
import traceback

from IPython.terminal import pt_inputhooks
from IPython.terminal.embed import InteractiveShellEmbed

# 从manimlib的动画淡入淡出模块导入VFadeInThenOut类
# 该类用于创建先淡入后淡出的动画效果，适用于需要临时显示的元素
from manimlib.animation.fading import VFadeInThenOut

# 从manimlib配置模块导入manim_config对象
# 该对象存储了Manim的配置信息，可用于访问或修改渲染参数、路径设置等
from manimlib.config import manim_config

# 从manimlib常量模块导入RED常量
# 这是Manim预定义的红色颜色常量，用于设置图形元素的颜色
from manimlib.constants import RED

# 从manimlib的mobject模块导入Mobject类
# Mobject是Manim中所有可渲染对象的基类，所有图形元素都继承自此类
from manimlib.mobject.mobject import Mobject

# 从manimlib的mobject模块导入FullScreenRectangle类
# 该类用于创建一个覆盖整个屏幕的矩形对象，常用于背景设置等场景
from manimlib.mobject.frame import FullScreenRectangle

# 从manimlib导入ModuleLoader类
# 该类用于加载Manim相关的模块和场景，处理导入和加载逻辑
from manimlib.module_loader import ModuleLoader


# 导入类型检查模块，仅在类型检查时生效（不影响运行时）
from typing import TYPE_CHECKING
# 当进行类型检查时，导入Scene类（避免运行时循环导入问题）
if TYPE_CHECKING:
    from manimlib.scene.scene import Scene


# 定义交互式场景嵌入类，用于在Manim场景中嵌入IPython交互终端
class InteractiveSceneEmbed:
    # 类初始化方法，接收一个Scene实例作为参数
    def __init__(self, scene: Scene):
        # 保存传入的场景实例，后续交互操作基于该场景
        self.scene = scene
        # 创建检查点管理器实例，用于管理场景状态的检查点（保存/恢复）
        self.checkpoint_manager = CheckpointManager()

        # 获取用于嵌入场景的IPython交互shell
        self.shell = self.get_ipython_shell_for_embedded_scene()
        # 启用GUI交互（确保嵌入期间场景窗口可响应操作）
        self.enable_gui()
        # 确保IPython单元格执行后更新场景帧（避免界面卡顿）
        self.ensure_frame_update_post_cell()
        # 确保发生异常时场景有视觉反馈（如红色边框闪烁）
        self.ensure_flash_on_error()
        # 如果配置中开启了自动重载，执行自动重载逻辑
        if manim_config.embed.autoreload:
            self.auto_reload()

    # 启动IPython嵌入终端的方法
    def launch(self):
        # 执行IPython shell，进入交互模式
        self.shell()

    # 创建并配置用于嵌入场景的IPython交互shell
    def get_ipython_shell_for_embedded_scene(self) -> InteractiveShellEmbed:
        """
        创建配置为可访问调用者局部命名空间的嵌入式IPython终端
        """
        # 回溯调用栈：向上三层找到用户场景定义中调用"self.embed"的上下文
        # （第一层：当前方法，第二层：__init__，第三层：用户场景中的embed调用）
        caller_frame = inspect.currentframe().f_back.f_back.f_back

        # 获取调用者所在的模块（通过调用帧的全局变量__file__定位模块）
        module = ModuleLoader.get_module(caller_frame.f_globals["__file__"])
        # 将调用者的局部变量更新到模块命名空间（让IPython能访问用户定义的变量）
        module.__dict__.update(caller_frame.f_locals)
        # 将自定义快捷函数更新到模块命名空间（方便用户在IPython中快速调用）
        module.__dict__.update(self.get_shortcuts())
        # 从配置中获取异常处理模式（用于IPython的错误显示）
        exception_mode = manim_config.embed.exception_mode

        # 创建并返回嵌入式IPython shell实例
        return InteractiveShellEmbed(
            user_module=module,  # 指定shell的用户模块（即调用者所在模块）
            display_banner=False,  # 不显示IPython默认启动横幅
            xmode=exception_mode  # 设置异常显示模式（如详细/简洁）
        )

    # 定义IPython交互终端中的自定义快捷函数
    def get_shortcuts(self):
        """
        在交互shell命名空间中添加几个实用的自定义快捷函数
        """
        # 简化场景实例引用（避免重复写self.scene）
        scene = self.scene
        # 返回快捷函数字典：键为函数名，值为对应的场景方法或自定义方法
        return dict(
            play=scene.play,          # 快捷调用场景的动画播放方法
            wait=scene.wait,          # 快捷调用场景的等待方法
            add=scene.add,            # 快捷调用场景的对象添加方法
            remove=scene.remove,      # 快捷调用场景的对象移除方法
            clear=scene.clear,        # 快捷调用场景的对象清空方法
            focus=scene.focus,        # 快捷调用场景的相机聚焦方法
            save_state=scene.save_state,  # 快捷调用场景的状态保存方法
            undo=scene.undo,          # 快捷调用场景的撤销方法
            redo=scene.redo,          # 快捷调用场景的重做方法
            i2g=scene.i2g,            # 快捷调用场景的"图像转网格"方法（假设场景有此方法）
            i2m=scene.i2m,            # 快捷调用场景的"图像转图形"方法（假设场景有此方法）
            checkpoint_paste=self.checkpoint_paste,  # 快捷调用检查点粘贴方法
            clear_checkpoints=self.checkpoint_manager.clear_checkpoints,  # 快捷清空检查点
            reload=self.reload_scene  # 快捷调用场景重载方法（下方定义）
        )

    # 启用GUI交互，确保嵌入期间场景窗口可响应鼠标/键盘操作
    def enable_gui(self):
        """在嵌入期间启用GUI交互"""
        # 定义IPython的输入钩子函数：在等待用户输入时更新场景
        def inputhook(context):
            # 当IPython未准备好接收输入时（即等待用户操作时）
            while not context.input_is_ready():
                # 如果场景窗口未关闭，更新场景帧（dt=0表示无时间流逝，仅刷新画面）
                if not self.scene.is_window_closing():
                    self.scene.update_frame(dt=0)
            # 如果场景窗口被关闭，触发IPython退出
            if self.scene.is_window_closing():
                self.shell.ask_exit()

        # 注册自定义输入钩子到IPython，命名为"manim"
        pt_inputhooks.register("manim", inputhook)
        # 启用"manim"类型的GUI，让IPython使用自定义输入钩子
        self.shell.enable_gui("manim")

    # 确保IPython单元格执行后强制更新场景帧，避免界面停滞
    def ensure_frame_update_post_cell(self):
        """确保每个IPython单元格执行后更新场景帧"""
        # 定义单元格执行后的回调函数
        def post_cell_func(*args, **kwargs):
            # 如果场景窗口未关闭，强制更新场景帧（force_draw=True确保重新绘制）
            if not self.scene.is_window_closing():
                self.scene.update_frame(dt=0, force_draw=True)

        # 注册回调函数到IPython的"post_run_cell"事件（单元格执行后触发）
        self.shell.events.register("post_run_cell", post_cell_func)

    # 配置异常处理：发生异常时场景显示红色边框闪烁（可选播放提示音）
    def ensure_flash_on_error(self):
        """发生异常时闪烁边框，并可能播放提示音"""
        # 定义自定义异常处理函数
        def custom_exc(shell, etype, evalue, tb, tb_offset=None):
            # 先显示异常信息，不吞掉错误（保持IPython默认错误追踪）
            shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)
            # 创建全屏红色边框矩形（无填充，仅30像素宽的红色边框）
            rect = FullScreenRectangle().set_stroke(RED, 30).set_fill(opacity=0)
            # 固定矩形在场景框架中（不随相机移动）
            rect.fix_in_frame()
            # 播放矩形"淡入后淡出"的动画（持续0.5秒），作为异常视觉提示
            self.scene.play(VFadeInThenOut(rect, run_time=0.5))

        # 为所有Exception类型注册自定义异常处理函数（覆盖默认处理）
        self.shell.set_custom_exc((Exception,), custom_exc)

    def reload_scene(self, embed_line: int | None = None) -> None:
        """
        Reloads the scene just like the `manimgl` command would do with the
        same arguments that were provided for the initial startup. This allows
        for quick iteration during scene development since we don't have to exit
        the IPython kernel and re-run the `manimgl` command again. The GUI stays
        open during the reload.

        If `embed_line` is provided, the scene will be reloaded at that line
        number. This corresponds to the `linemarker` param of the
        `extract_scene.insert_embed_line_to_module()` method.

        Before reload, the scene is cleared and the entire state is reset, such
        that we can start from a clean slate. This is taken care of by the
        run_scenes function in __main__.py, which will catch the error raised by the
        `exit_raise` magic command that we invoke here.

        Note that we cannot define a custom exception class for this error,
        since the IPython kernel will swallow any exception. While we can catch
        such an exception in our custom exception handler registered with the
        `set_custom_exc` method, we cannot break out of the IPython shell by
        this means.
        """
        # Update the global run configuration.
        run_config = manim_config.run
        run_config.is_reload = True
        if embed_line:
            run_config.embed_line = embed_line

        print("Reloading...")
        self.shell.run_line_magic("exit_raise", "")

    def auto_reload(self):
        """Enables reload the shell's module before all calls"""
        def pre_cell_func(*args, **kwargs):
            new_mod = ModuleLoader.get_module(self.shell.user_module.__file__, is_during_reload=True)
            self.shell.user_ns.update(vars(new_mod))

        self.shell.events.register("pre_run_cell", pre_cell_func)

    def checkpoint_paste(
        self,
        skip: bool = False,
        record: bool = False,
        progress_bar: bool = True
    ):
        with self.scene.temp_config_change(skip, record, progress_bar):
            self.checkpoint_manager.checkpoint_paste(self.shell, self.scene)


class CheckpointManager:
    def __init__(self):
        self.checkpoint_states: dict[str, list[tuple[Mobject, Mobject]]] = dict()

    def checkpoint_paste(self, shell, scene):
        """
        Used during interactive development to run (or re-run)
        a block of scene code.

        If the copied selection starts with a comment, this will
        revert to the state of the scene the first time this function
        was called on a block of code starting with that comment.
        """
        code_string = pyperclip.paste()
        checkpoint_key = self.get_leading_comment(code_string)
        self.handle_checkpoint_key(scene, checkpoint_key)
        shell.run_cell(code_string)

    @staticmethod
    def get_leading_comment(code_string: str) -> str:
        leading_line = code_string.partition("\n")[0].lstrip()
        if leading_line.startswith("#"):
            return leading_line
        return ""

    def handle_checkpoint_key(self, scene, key: str):
        if not key:
            return
        elif key in self.checkpoint_states:
            # Revert to checkpoint
            scene.restore_state(self.checkpoint_states[key])

            # Clear out any saved states that show up later
            all_keys = list(self.checkpoint_states.keys())
            index = all_keys.index(key)
            for later_key in all_keys[index + 1:]:
                self.checkpoint_states.pop(later_key)
        else:
            self.checkpoint_states[key] = scene.get_state()

    def clear_checkpoints(self):
        self.checkpoint_states = dict()
