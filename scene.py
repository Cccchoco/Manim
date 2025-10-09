from __future__ import annotations

from collections import OrderedDict
import platform  # 用于获取操作系统信息
import random  # 用于随机数生成
import time  # 用于时间相关操作
from functools import wraps  # 用于装饰器
from contextlib import contextmanager  # 用于上下文管理器
from contextlib import ExitStack  # 用于管理多个上下文

import numpy as np  # 用于数值计算
from tqdm.auto import tqdm as ProgressDisplay  # 用于显示进度条
from pyglet.window import key as PygletWindowKeys  # 导入pyglet的按键常量

from manimlib.animation.animation import prepare_animation  # 用于准备动画
from manimlib.camera.camera import Camera  # 相机类
from manimlib.camera.camera_frame import CameraFrame  # 相机帧类
from manimlib.config import manim_config  # manim配置
from manimlib.event_handler import EVENT_DISPATCHER  # 事件分发器
from manimlib.event_handler.event_type import EventType  # 事件类型
from manimlib.logger import log  # 日志工具
from manimlib.mobject.mobject import _AnimationBuilder  # 动画构建器
from manimlib.mobject.mobject import Group  # 图形组类
from manimlib.mobject.mobject import Mobject  # 基础图形类
from manimlib.mobject.mobject import Point  # 点图形类
from manimlib.mobject.types.vectorized_mobject import VGroup  # 向量图形组类
from manimlib.mobject.types.vectorized_mobject import VMobject  # 向量图形类
from manimlib.scene.scene_embed import InteractiveSceneEmbed  # 交互式场景嵌入
from manimlib.scene.scene_embed import CheckpointManager  # 检查点管理器
from manimlib.scene.scene_file_writer import SceneFileWriter  # 场景文件写入器
from manimlib.utils.dict_ops import merge_dicts_recursively  # 递归合并字典
from manimlib.utils.family_ops import extract_mobject_family_members  # 提取图形家族成员
from manimlib.utils.family_ops import recursive_mobject_remove  # 递归移除图形
from manimlib.utils.iterables import batch_by_property  # 按属性批量处理
from manimlib.utils.sounds import play_sound  # 播放声音
from manimlib.utils.color import color_to_rgba  # 颜色转换为RGBA
from manimlib.window import Window  # 窗口类

from typing import TYPE_CHECKING  # 用于类型提示的条件导入

# 类型检查时导入所需的类，避免循环导入问题
if TYPE_CHECKING:
    from typing import Callable, Iterable, TypeVar, Optional
    from manimlib.typing import Vect3

    T = TypeVar('T')

    from PIL.Image import Image

    from manimlib.animation.animation import Animation


class Scene(object):
    """场景类，是所有动画场景的基类，管理图形、动画和交互"""
    
    random_seed: int = 0  # 随机数种子，确保场景的可重复性
    pan_sensitivity: float = 0.5  # 平移灵敏度
    scroll_sensitivity: float = 20  # 滚动灵敏度
    drag_to_pan: bool = True  # 是否通过拖拽来平移视图
    max_num_saved_states: int = 50  # 最大保存状态数
    default_camera_config: dict = dict()  # 默认相机配置
    default_file_writer_config: dict = dict()  # 默认文件写入器配置
    samples = 0  # 采样数（用于抗锯齿等）
    # 欧拉角，以度为单位（用于相机初始方向）
    default_frame_orientation = (0, 0)

    def __init__(
        self,
        window: Optional[Window] = None,  # 窗口对象
        camera_config: dict = dict(),  # 相机配置
        file_writer_config: dict = dict(),  # 文件写入器配置
        skip_animations: bool = False,  # 是否跳过动画
        always_update_mobjects: bool = False,  # 是否总是更新图形
        start_at_animation_number: int | None = None,  # 从哪个动画编号开始
        end_at_animation_number: int | None = None,  # 到哪个动画编号结束
        show_animation_progress: bool = False,  # 是否显示动画进度
        leave_progress_bars: bool = False,  # 是否保留进度条
        preview_while_skipping: bool = True,  # 跳过动画时是否预览
        presenter_mode: bool = False,  # 是否演示者模式
        default_wait_time: float = 1.0,  # 默认等待时间
    ):
        self.skip_animations = skip_animations  # 是否跳过动画
        self.always_update_mobjects = always_update_mobjects  # 是否总是更新图形
        self.start_at_animation_number = start_at_animation_number  # 开始动画编号
        self.end_at_animation_number = end_at_animation_number  # 结束动画编号
        self.show_animation_progress = show_animation_progress  # 显示动画进度
        self.leave_progress_bars = leave_progress_bars  # 保留进度条
        self.preview_while_skipping = preview_while_skipping  # 跳过动画时预览
        self.presenter_mode = presenter_mode  # 演示者模式
        self.default_wait_time = default_wait_time  # 默认等待时间

        # 合并相机配置：全局默认 -> 类默认 -> 实例参数
        self.camera_config = merge_dicts_recursively(
            manim_config.camera,         # 全局默认配置
            self.default_camera_config,  # 类定义的默认配置
            camera_config,               # 实例化时传入的配置
        )
        # 合并文件写入器配置：全局默认 -> 类默认 -> 实例参数
        self.file_writer_config = merge_dicts_recursively(
            manim_config.file_writer,
            self.default_file_writer_config,
            file_writer_config,
        )

        self.window = window  # 窗口对象
        if self.window:
            self.window.init_for_scene(self)  # 为场景初始化窗口
            # 确保相机和Pyglet窗口同步，设置帧率为30
            self.camera_config["fps"] = 30

        # 场景的核心状态
        self.camera: Camera = Camera(
            window=self.window,
            samples=self.samples,
            **self.camera_config  # 应用相机配置
        )
        self.frame: CameraFrame = self.camera.frame  # 相机帧（决定视图）
        self.frame.reorient(*self.default_frame_orientation)  # 应用默认方向
        self.frame.make_orientation_default()  # 将当前方向设为默认

        # 初始化文件写入器
        self.file_writer = SceneFileWriter(self,** self.file_writer_config)
        # 场景中的图形列表，初始包含相机帧
        self.mobjects: list[Mobject] = [self.camera.frame]
        self.render_groups: list[Mobject] = []  # 渲染组列表
        self.id_to_mobject_map: dict[int, Mobject] = dict()  # 图形ID到图形的映射
        self.num_plays: int = 0  # 播放次数计数
        self.time: float = 0  # 场景时间
        self.skip_time: float = 0  # 跳过的时间
        self.original_skipping_status: bool = self.skip_animations  # 初始跳过状态
        self.undo_stack = []  # 撤销栈
        self.redo_stack = []  # 重做栈

        # 如果指定了开始动画编号，则跳过动画
        if self.start_at_animation_number is not None:
            self.skip_animations = True
        # 如果文件写入器有进度显示，则不显示动画进度
        if self.file_writer.has_progress_display():
            self.show_animation_progress = False

        # 交互相关项
        self.mouse_point = Point()  # 鼠标位置点
        self.mouse_drag_point = Point()  # 鼠标拖拽点
        self.hold_on_wait = self.presenter_mode  # 在等待时是否保持（演示者模式）
        self.quit_interaction = False  # 是否退出交互

        # 设置随机种子，确保场景的可重复性
        if self.random_seed is not None:
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)
    def __str__(self) -> str:
    # 返回当前类的名称作为字符串表示
    return self.__class__.__name__

def get_window(self) -> Window | None:
    # 返回当前场景关联的窗口对象，可能为None
    return self.window

def run(self) -> None:
    # 初始化虚拟动画开始时间为0
    self.virtual_animation_start_time: float = 0
    # 记录实际动画开始的时间（当前系统时间）
    self.real_animation_start_time: float = time.time()
    # 通知文件写入器开始工作
    self.file_writer.begin()

    # 调用设置方法
    self.setup()
    try:
        # 调用构建场景方法（子类实现具体动画内容）
        self.construct()
        # 进入交互模式
        self.interact()
    except EndScene:
        # 捕获结束场景异常，不做处理直接忽略
        pass
    except KeyboardInterrupt:
        # 捕获键盘中断（如Ctrl+C）
        # 清除键盘中断显示的符号
        print("", end="\r")
        # 标记文件写入器因中断而结束
        self.file_writer.ended_with_interrupt = True
    # 调用清理方法
    self.tear_down()

def setup(self) -> None:
    """
    这个方法旨在由任何通常被继承的场景实现，
    在调用construct方法之前进行一些通用的设置工作。
    """
    pass

def construct(self) -> None:
    # 所有动画发生的地方
    # 需在子类中实现
    pass

def tear_down(self) -> None:
    # 停止跳过动画
    self.stop_skipping()
    # 通知文件写入器完成工作
    self.file_writer.finish()
    # 如果存在窗口对象
    if self.window:
        # 销毁窗口
        self.window.destroy()
        # 将窗口引用设为None
        self.window = None

def interact(self) -> None:
    """
    如果存在窗口，进入一个循环，
    在内部调用pyglet事件循环的同时更新帧
    """
    # 如果没有窗口则直接返回
    if self.window is None:
        return
    # 输出提示信息
    log.info(
        "\nTips: Using the keys `d`, `f`, or `z` " +
        "you can interact with the scene. " +
        "Press `command + q` or `esc` to quit"
    )
    # 初始化跳过动画标志为False
    self.skip_animations = False
    # 当窗口未关闭时持续循环
    while not self.is_window_closing():
        # 以相机帧率的倒数作为时间间隔更新帧
        self.update_frame(1 / self.camera.fps)

def embed(
    self,
    close_scene_on_exit: bool = True,
    show_animation_progress: bool = False,
) -> None:
    # 如果没有窗口，嵌入功能不适用，直接返回
    if not self.window:
        # 嵌入仅与带有窗口的交互式开发相关
        return
    # 设置是否显示动画进度
    self.show_animation_progress = show_animation_progress
    # 停止跳过动画
    self.stop_skipping()
    # 强制绘制更新帧
    self.update_frame(force_draw=True)

    # 启动交互式场景嵌入
    InteractiveSceneEmbed(self).launch()

    # 当退出嵌入时关闭场景
    if close_scene_on_exit:
        raise EndScene()

# 只有这些方法应该接触相机

def get_image(self) -> Image:
    # 如果窗口存在
    if self.window is not None:
        # 告诉相机不要使用窗口的帧缓冲区
        self.camera.use_window_fbo(False)
        # 让相机捕获所有渲染组的内容
        self.camera.capture(*self.render_groups)
    # 从相机获取图像
    image = self.camera.get_image()
    # 如果窗口存在
    if self.window is not None:
        # 告诉相机使用窗口的帧缓冲区
        self.camera.use_window_fbo(True)
    # 返回获取的图像
    return image

def show(self) -> None:
    # 强制绘制更新帧
    self.update_frame(force_draw=True)
    # 获取图像并显示
    self.get_image().show()

def update_frame(self, dt: float = 0, force_draw: bool = False) -> None:
    # 增加时间
    self.increment_time(dt)
    # 更新所有可移动对象
    self.update_mobjects(dt)
    # 如果跳过动画且不强制绘制，则返回
    if self.skip_animations and not force_draw:
        return

    # 如果窗口正在关闭，抛出结束场景异常
    if self.is_window_closing():
        raise EndScene()

    # 如果窗口存在，且时间间隔为0，且没有未绘制的事件，且不强制绘制
    if self.window and dt == 0 and not self.window.has_undrawn_event() and not force_draw:
        # 在这种情况下，不需要新的渲染，但仍应监听新事件
        self.window._window.dispatch_events()
        return

    # 让相机捕获所有渲染组的内容
    self.camera.capture(*self.render_groups)

    # 如果窗口存在且不跳过动画
    if self.window and not self.skip_animations:
        # 计算虚拟动画时间（当前时间减去虚拟动画开始时间）
        vt = self.time - self.virtual_animation_start_time
        # 计算实际动画时间（当前系统时间减去实际动画开始时间）
        rt = time.time() - self.real_animation_start_time
        # 确保虚拟时间不超过实际时间，必要时休眠
        time.sleep(max(vt - rt, 0))

def emit_frame(self) -> None:
    # 如果不跳过动画
    if not self.skip_animations:
        # 让文件写入器写入当前相机捕获的帧
        self.file_writer.write_frame(self.camera)

# 与更新相关的方法

def update_mobjects(self, dt: float) -> None:
    # 遍历所有可移动对象
    for mobject in self.mobjects:
        # 调用每个对象的更新方法，传入时间间隔
        mobject.update(dt)

def should_update_mobjects(self) -> bool:
    # 如果始终更新可移动对象，或者任何可移动对象有更新器，则返回True
    return self.always_update_mobjects or any(
        mob.has_updaters() for mob in self.mobjects
    )

# 与时间相关的方法

def get_time(self) -> float:
    # 返回当前时间
    return self.time

def increment_time(self, dt: float) -> None:
    # 增加时间，加上时间间隔dt
    self.time += dt

# 与内部可移动对象组织相关的方法

def get_top_level_mobjects(self) -> list[Mobject]:
    # 返回那些不在场景中其他可移动对象家族中的顶级可移动对象
    mobjects = self.get_mobjects()
    # 获取每个可移动对象的家族（包括自身和子对象）
    families = [m.get_family() for m in mobjects]

    def is_top_level(mobject):
        # 计算该可移动对象属于多少个家族
        num_families = sum([
            (mobject in family)
            for family in families
        ])
        # 只属于自身家族的才是顶级对象
        return num_families == 1
    # 过滤并返回顶级可移动对象列表
    return list(filter(is_top_level, mobjects))

def get_mobject_family_members(self) -> list[Mobject]:
    # 提取所有可移动对象的家族成员并返回
    return extract_mobject_family_members(self.mobjects)

def assemble_render_groups(self):
    """
    当相同类型的可移动对象组合在一起时，渲染会更高效，
    因此这个函数创建场景中所有相邻可移动对象集群的组
    """
    # 按特定属性对可移动对象进行分组
    batches = batch_by_property(
        self.mobjects,
        # 分组键：类型字符串 + 着色器包装器ID + z轴索引
        lambda m: str(type(m)) + str(m.get_shader_wrapper(self.camera.ctx).get_id()) + str(m.z_index)
    )

    # 清空现有的渲染组
    for group in self.render_groups:
        group.clear()
    # 重新创建渲染组：为每个批次创建对应的组
    self.render_groups = [
        batch[0].get_group_class()(*batch)
        for batch, key in batches
    ]

    @staticmethod
    def affects_mobject_list(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.assemble_render_groups()
            return self
        return wrapper

    @affects_mobject_list
    def add(self, *new_mobjects: Mobject):
        """
        Mobjects will be displayed, from background to
        foreground in the order with which they are added.
        """
        self.remove(*new_mobjects)
        self.mobjects += new_mobjects

        # Reorder based on z_index
        id_to_scene_order = {id(m): idx for idx, m in enumerate(self.mobjects)}
        self.mobjects.sort(key=lambda m: (m.z_index, id_to_scene_order[id(m)]))

        self.id_to_mobject_map.update({
            id(sm): sm
            for m in new_mobjects
            for sm in m.get_family()
        })
        return self

    def add_mobjects_among(self, values: Iterable):
        """
        This is meant mostly for quick prototyping,
        e.g. to add all mobjects defined up to a point,
        call self.add_mobjects_among(locals().values())
        """
        self.add(*filter(
            lambda m: isinstance(m, Mobject),
            values
        ))
        return self

    @affects_mobject_list
    def replace(self, mobject: Mobject, *replacements: Mobject):
        if mobject in self.mobjects:
            index = self.mobjects.index(mobject)
            self.mobjects = [
                *self.mobjects[:index],
                *replacements,
                *self.mobjects[index + 1:]
            ]
        return self

    @affects_mobject_list
    def remove(self, *mobjects_to_remove: Mobject):
        """
        Removes anything in mobjects from scenes mobject list, but in the event that one
        of the items to be removed is a member of the family of an item in mobject_list,
        the other family members are added back into the list.

        For example, if the scene includes Group(m1, m2, m3), and we call scene.remove(m1),
        the desired behavior is for the scene to then include m2 and m3 (ungrouped).
        """
        to_remove = set(extract_mobject_family_members(mobjects_to_remove))
        new_mobjects, _ = recursive_mobject_remove(self.mobjects, to_remove)
        self.mobjects = new_mobjects

    @affects_mobject_list
    def remove_all_except(self, *mobjects_to_keep : Mobject):
        self.clear()
        self.add(*mobjects_to_keep)

    def bring_to_front(self, *mobjects: Mobject):
        self.add(*mobjects)
        return self

    @affects_mobject_list
    def bring_to_back(self, *mobjects: Mobject):
        self.remove(*mobjects)
        self.mobjects = list(mobjects) + self.mobjects
        return self

    @affects_mobject_list
    def clear(self):
        self.mobjects = []
        return self

    def get_mobjects(self) -> list[Mobject]:
        return list(self.mobjects)

    def get_mobject_copies(self) -> list[Mobject]:
        return [m.copy() for m in self.mobjects]

    def point_to_mobject(
        self,
        point: np.ndarray,
        search_set: Iterable[Mobject] | None = None,
        buff: float = 0
    ) -> Mobject | None:
        """
        E.g. if clicking on the scene, this returns the top layer mobject
        under a given point
        """
        if search_set is None:
            search_set = self.mobjects
        for mobject in reversed(search_set):
            if mobject.is_point_touching(point, buff=buff):
                return mobject
        return None

    def get_group(self, *mobjects):
        if all(isinstance(m, VMobject) for m in mobjects):
            return VGroup(*mobjects)
        else:
            return Group(*mobjects)

    def id_to_mobject(self, id_value):
        return self.id_to_mobject_map[id_value]

    def ids_to_group(self, *id_values):
        return self.get_group(*filter(
            lambda x: x is not None,
            map(self.id_to_mobject, id_values)
        ))

    def i2g(self, *id_values):
        return self.ids_to_group(*id_values)

    def i2m(self, id_value):
        return self.id_to_mobject(id_value)

    # Related to skipping

    def update_skipping_status(self) -> None:
        if self.start_at_animation_number is not None:
            if self.num_plays == self.start_at_animation_number:
                self.skip_time = self.time
                if not self.original_skipping_status:
                    self.stop_skipping()
        if self.end_at_animation_number is not None:
            if self.num_plays >= self.end_at_animation_number:
                raise EndScene()

    def stop_skipping(self) -> None:
        self.virtual_animation_start_time = self.time
        self.real_animation_start_time = time.time()
        self.skip_animations = False

    # Methods associated with running animations

    def get_time_progression(
        self,
        run_time: float,
        n_iterations: int | None = None,
        desc: str = "",
        override_skip_animations: bool = False
    ) -> list[float] | np.ndarray | ProgressDisplay:
        if self.skip_animations and not override_skip_animations:
            return [run_time]

        times = np.arange(0, run_time, 1 / self.camera.fps) + 1 / self.camera.fps

        self.file_writer.set_progress_display_description(sub_desc=desc)

        if self.show_animation_progress:
            return ProgressDisplay(
                times,
                total=n_iterations,
                leave=self.leave_progress_bars,
                ascii=True if platform.system() == 'Windows' else None,
                desc=desc,
                bar_format="{l_bar} {n_fmt:3}/{total_fmt:3} {rate_fmt}{postfix}",
            )
        else:
            return times

    def get_run_time(self, animations: Iterable[Animation]) -> float:
        return np.max([animation.get_run_time() for animation in animations])

    def get_animation_time_progression(
        self,
        animations: Iterable[Animation]
    ) -> list[float] | np.ndarray | ProgressDisplay:
        animations = list(animations)
        run_time = self.get_run_time(animations)
        description = f"{self.num_plays} {animations[0]}"
        if len(animations) > 1:
            description += ", etc."
        time_progression = self.get_time_progression(run_time, desc=description)
        return time_progression

    def get_wait_time_progression(
        self,
        duration: float,
        stop_condition: Callable[[], bool] | None = None
    ) -> list[float] | np.ndarray | ProgressDisplay:
        kw = {"desc": f"{self.num_plays} Waiting"}
        if stop_condition is not None:
            kw["n_iterations"] = -1  # So it doesn't show % progress
            kw["override_skip_animations"] = True
        return self.get_time_progression(duration, **kw)

    def pre_play(self):
        if self.presenter_mode and self.num_plays == 0:
            self.hold_loop()

        self.update_skipping_status()

        if not self.skip_animations:
            self.file_writer.begin_animation()

        if self.window:
            self.virtual_animation_start_time = self.time
            self.real_animation_start_time = time.time()

    def post_play(self):
        if not self.skip_animations:
            self.file_writer.end_animation()

        if self.preview_while_skipping and self.skip_animations and self.window is not None:
            # Show some quick frames along the way
            self.update_frame(dt=0, force_draw=True)

        self.num_plays += 1

    def begin_animations(self, animations: Iterable[Animation]) -> None:
        all_mobjects = set(self.get_mobject_family_members())
        for animation in animations:
            animation.begin()
            # Anything animated that's not already in the
            # scene gets added to the scene.  Note, for
            # animated mobjects that are in the family of
            # those on screen, this can result in a restructuring
            # of the scene.mobjects list, which is usually desired.
            if animation.mobject not in all_mobjects:
                self.add(animation.mobject)
                all_mobjects = all_mobjects.union(animation.mobject.get_family())

    def progress_through_animations(self, animations: Iterable[Animation]) -> None:
        last_t = 0
        for t in self.get_animation_time_progression(animations):
            dt = t - last_t
            last_t = t
            for animation in animations:
                animation.update_mobjects(dt)
                alpha = t / animation.run_time
                animation.interpolate(alpha)
            self.update_frame(dt)
            self.emit_frame()

    def finish_animations(self, animations: Iterable[Animation]) -> None:
        for animation in animations:
            animation.finish()
            animation.clean_up_from_scene(self)
        if self.skip_animations:
            self.update_mobjects(self.get_run_time(animations))
        else:
            self.update_mobjects(0)

    @affects_mobject_list
    def play(
        self,
        *proto_animations: Animation | _AnimationBuilder,
        run_time: float | None = None,
        rate_func: Callable[[float], float] | None = None,
        lag_ratio: float | None = None,
    ) -> None:
        if len(proto_animations) == 0:
            log.warning("Called Scene.play with no animations")
            return
        animations = list(map(prepare_animation, proto_animations))
        for anim in animations:
            anim.update_rate_info(run_time, rate_func, lag_ratio)
        self.pre_play()
        self.begin_animations(animations)
        self.progress_through_animations(animations)
        self.finish_animations(animations)
        self.post_play()

    def wait(
        self,
        duration: Optional[float] = None,
        stop_condition: Callable[[], bool] = None,
        note: str = None,
        ignore_presenter_mode: bool = False
    ):
        if duration is None:
            duration = self.default_wait_time
        self.pre_play()
        self.update_mobjects(dt=0)  # Any problems with this?
        if self.presenter_mode and not self.skip_animations and not ignore_presenter_mode:
            if note:
                log.info(note)
            self.hold_loop()
        else:
            time_progression = self.get_wait_time_progression(duration, stop_condition)
            last_t = 0
            for t in time_progression:
                dt = t - last_t
                last_t = t
                self.update_frame(dt)
                self.emit_frame()
                if stop_condition is not None and stop_condition():
                    break
        self.post_play()

    def hold_loop(self):
        while self.hold_on_wait:
            self.update_frame(dt=1 / self.camera.fps)
        self.hold_on_wait = True

    def wait_until(
        self,
        stop_condition: Callable[[], bool],
        max_time: float = 60
    ):
        self.wait(max_time, stop_condition=stop_condition)

    def force_skipping(self):
        self.original_skipping_status = self.skip_animations
        self.skip_animations = True
        return self

    def revert_to_original_skipping_status(self):
        if hasattr(self, "original_skipping_status"):
            self.skip_animations = self.original_skipping_status
        return self

    def add_sound(
        self,
        sound_file: str,
        time_offset: float = 0,
        gain: float | None = None,
        gain_to_background: float | None = None
    ):
        if self.skip_animations:
            return
        time = self.get_time() + time_offset
        self.file_writer.add_sound(sound_file, time, gain, gain_to_background)

    # Helpers for interactive development

    def get_state(self) -> SceneState:
        return SceneState(self)

    @affects_mobject_list
    def restore_state(self, scene_state: SceneState):
        scene_state.restore_scene(self)

    def save_state(self) -> None:
        state = self.get_state()
        if self.undo_stack and state.mobjects_match(self.undo_stack[-1]):
            return
        self.redo_stack = []
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_num_saved_states:
            self.undo_stack.pop(0)

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.get_state())
            self.restore_state(self.undo_stack.pop())

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.get_state())
            self.restore_state(self.redo_stack.pop())

    @contextmanager
    def temp_skip(self):
        prev_status = self.skip_animations
        self.skip_animations = True
        try:
            yield
        finally:
            if not prev_status:
                self.stop_skipping()

    @contextmanager
    def temp_progress_bar(self):
        prev_progress = self.show_animation_progress
        self.show_animation_progress = True
        try:
            yield
        finally:
            self.show_animation_progress = prev_progress

    @contextmanager
    def temp_record(self):
        self.camera.use_window_fbo(False)
        self.file_writer.begin_insert()
        try:
            yield
        finally:
            self.file_writer.end_insert()
            self.camera.use_window_fbo(True)

    def temp_config_change(self, skip=False, record=False, progress_bar=False):
        stack = ExitStack()
        if skip:
            stack.enter_context(self.temp_skip())
        if record:
            stack.enter_context(self.temp_record())
        if progress_bar:
            stack.enter_context(self.temp_progress_bar())
        return stack

    def is_window_closing(self):
        return self.window and (self.window.is_closing or self.quit_interaction)

    # Event handling
    def set_floor_plane(self, plane: str = "xy"):
        if plane == "xy":
            self.frame.set_euler_axes("zxz")
        elif plane == "xz":
            self.frame.set_euler_axes("zxy")
        else:
            raise Exception("Only `xz` and `xy` are valid floor planes")

    def on_mouse_motion(
        self,
        point: Vect3,
        d_point: Vect3
    ) -> None:
        assert self.window is not None
        self.mouse_point.move_to(point)

        event_data = {"point": point, "d_point": d_point}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MouseMotionEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

        frame = self.camera.frame
        # Handle perspective changes
        if self.window.is_key_pressed(ord(manim_config.key_bindings.pan_3d)):
            ff_d_point = frame.to_fixed_frame_point(d_point, relative=True)
            ff_d_point *= self.pan_sensitivity
            frame.increment_theta(-ff_d_point[0])
            frame.increment_phi(ff_d_point[1])
        # Handle frame movements
        elif self.window.is_key_pressed(ord(manim_config.key_bindings.pan)):
            frame.shift(-d_point)

    def on_mouse_drag(
        self,
        point: Vect3,
        d_point: Vect3,
        buttons: int,
        modifiers: int
    ) -> None:
        self.mouse_drag_point.move_to(point)
        if self.drag_to_pan:
            self.frame.shift(-d_point)

        event_data = {"point": point, "d_point": d_point, "buttons": buttons, "modifiers": modifiers}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MouseDragEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

    def on_mouse_press(
        self,
        point: Vect3,
        button: int,
        mods: int
    ) -> None:
        self.mouse_drag_point.move_to(point)
        event_data = {"point": point, "button": button, "mods": mods}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MousePressEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

    def on_mouse_release(
        self,
        point: Vect3,
        button: int,
        mods: int
    ) -> None:
        event_data = {"point": point, "button": button, "mods": mods}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MouseReleaseEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

    def on_mouse_scroll(
        self,
        point: Vect3,
        offset: Vect3,
        x_pixel_offset: float,
        y_pixel_offset: float
    ) -> None:
        event_data = {"point": point, "offset": offset}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.MouseScrollEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

        rel_offset = y_pixel_offset / self.camera.get_pixel_height()
        self.frame.scale(
            1 - self.scroll_sensitivity * rel_offset,
            about_point=point
        )

    def on_key_release(
        self,
        symbol: int,
        modifiers: int
    ) -> None:
        event_data = {"symbol": symbol, "modifiers": modifiers}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.KeyReleaseEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

    def on_key_press(
        self,
        symbol: int,
        modifiers: int
    ) -> None:
        try:
            char = chr(symbol)
        except OverflowError:
            log.warning("The value of the pressed key is too large.")
            return

        event_data = {"symbol": symbol, "modifiers": modifiers}
        propagate_event = EVENT_DISPATCHER.dispatch(EventType.KeyPressEvent, **event_data)
        if propagate_event is not None and propagate_event is False:
            return

        if char == manim_config.key_bindings.reset:
            self.play(self.camera.frame.animate.to_default_state())
        elif char == "z" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
            self.undo()
        elif char == "z" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL | PygletWindowKeys.MOD_SHIFT)):
            self.redo()
        # command + q
        elif char == manim_config.key_bindings.quit and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
            self.quit_interaction = True
        # Space or right arrow
        elif char == " " or symbol == PygletWindowKeys.RIGHT:
            self.hold_on_wait = False

    def on_resize(self, width: int, height: int) -> None:
        pass

    def on_show(self) -> None:
        pass

    def on_hide(self) -> None:
        pass

    def on_close(self) -> None:
        pass

    def focus(self) -> None:
        """
        Puts focus on the ManimGL window.
        """
        if not self.window:
            return
        self.window.focus()

    def set_background_color(self, background_color, background_opacity=1) -> None:
        self.camera.background_rgba = list(color_to_rgba(
            background_color, background_opacity
        ))


class SceneState():
    def __init__(self, scene: Scene, ignore: list[Mobject] | None = None):
        self.time = scene.time
        self.num_plays = scene.num_plays
        self.mobjects_to_copies = OrderedDict.fromkeys(scene.mobjects)
        if ignore:
            for mob in ignore:
                self.mobjects_to_copies.pop(mob, None)

        last_m2c = scene.undo_stack[-1].mobjects_to_copies if scene.undo_stack else dict()
        for mob in self.mobjects_to_copies:
            # If it hasn't changed since the last state, just point to the
            # same copy as before
            if mob in last_m2c and last_m2c[mob].looks_identical(mob):
                self.mobjects_to_copies[mob] = last_m2c[mob]
            else:
                self.mobjects_to_copies[mob] = mob.copy()

    def __eq__(self, state: SceneState):
        return all((
            self.time == state.time,
            self.num_plays == state.num_plays,
            self.mobjects_to_copies == state.mobjects_to_copies
        ))

    def mobjects_match(self, state: SceneState):
        return self.mobjects_to_copies == state.mobjects_to_copies

    def n_changes(self, state: SceneState):
        m2c = state.mobjects_to_copies
        return sum(
            1 - int(mob in m2c and mob.looks_identical(m2c[mob]))
            for mob in self.mobjects_to_copies
        )

    def restore_scene(self, scene: Scene):
        scene.time = self.time
        scene.num_plays = self.num_plays
        scene.mobjects = [
            mob.become(mob_copy)
            for mob, mob_copy in self.mobjects_to_copies.items()
        ]


class EndScene(Exception):
    pass


class ThreeDScene(Scene):
    samples = 4
    default_frame_orientation = (-30, 70)
    always_depth_test = True

    def add(self, *mobjects: Mobject, set_depth_test: bool = True, perp_stroke: bool = True):
        for mob in mobjects:
            if set_depth_test and not mob.is_fixed_in_frame() and self.always_depth_test:
                mob.apply_depth_test()
            if isinstance(mob, VMobject) and mob.has_stroke() and perp_stroke:
                mob.set_flat_stroke(False)
        super().add(*mobjects)
