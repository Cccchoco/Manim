# 导入未来版本的注解特性，允许在类型注解中使用尚未定义的类或类型
from __future__ import annotations

# 从copy模块导入deepcopy，用于创建对象的深拷贝
from copy import deepcopy

# 从manimlib的mobject模块导入动画构建器类和Mobject基类
from manimlib.mobject.mobject import _AnimationBuilder
from manimlib.mobject.mobject import Mobject

# 从工具模块导入移除列表冗余项的函数
from manimlib.utils.iterables import remove_list_redundancies

# 从速率函数模块导入平滑过渡函数
from manimlib.utils.rate_functions import smooth

# 从简单函数模块导入限制值范围的函数
from manimlib.utils.simple_functions import clip

# 从typing模块导入TYPE_CHECKING常量，用于条件导入类型
from typing import TYPE_CHECKING

# 仅在类型检查阶段执行的代码块（运行时不会执行）
if TYPE_CHECKING:
    # 从typing模块导入Callable类型，用于注解可调用对象
    from typing import Callable

    # 从scene模块导入Scene类，仅用于类型注解
    from manimlib.scene.scene import Scene


# 定义默认动画运行时间为1.0秒
DEFAULT_ANIMATION_RUN_TIME = 1.0
# 定义默认动画延迟比例为0（表示动画元素同时开始）
DEFAULT_ANIMATION_LAG_RATIO = 0


class Animation(object):
    """动画基类，所有具体动画类的父类，定义了动画的基本属性和行为"""
    
    def __init__(
        self,
        mobject: Mobject,
        run_time: float = DEFAULT_ANIMATION_RUN_TIME,
        # 动画运行的时间区间（元组形式）
        time_span: tuple[float, float] | None = None,
        # 延迟比例：
        # - 0表示所有子对象同时开始动画
        # - 1表示按顺序依次应用到每个子对象
        # - 0到1之间表示每个子对象按滞后时间依次开始
        lag_ratio: float = DEFAULT_ANIMATION_LAG_RATIO,
        rate_func: Callable[[float], float] = smooth,
        name: str = "",
        # 该动画是否在屏幕上添加或移除mobject
        remover: bool = False,
        # 动画完成时更新函数的最终alpha值
        final_alpha_value: float = 1.0,
        # 如果设为True，mobject自身的内部更新器会被调用，
        # 但起始或目标mobject不会被暂停。
        # 若要完全暂停更新，请在动画前调用mobject.suspend_updating()
        suspend_mobject_updating: bool = False,
    ):
        # 验证输入的mobject类型是否合法
        self._validate_input_type(mobject)
        # 动画作用的mobject（Manim中的可动画对象）
        self.mobject = mobject
        # 动画运行时间（秒），默认使用全局默认值
        self.run_time = run_time
        # 动画运行的时间区间，None表示使用默认时间线
        self.time_span = time_span
        # 速率函数，控制动画进度的变化速率（如平滑过渡、先快后慢等）
        self.rate_func = rate_func
        # 动画名称，默认使用"类名+对象标识"的形式
        self.name = name or self.__class__.__name__ + str(self.mobject)
        # 标记该动画是否用于移除mobject
        self.remover = remover
        # 动画结束时的最终alpha值（用于透明度等渐变属性）
        self.final_alpha_value = final_alpha_value
        # 子对象动画的延迟比例
        self.lag_ratio = lag_ratio
        # 是否暂停mobject的自动更新
        self.suspend_mobject_updating = suspend_mobject_updating

    def _validate_input_type(self, mobject: Mobject) -> None:
        if not isinstance(mobject, Mobject):
            raise TypeError("Animation only works for Mobjects.")

    def __str__(self) -> str:
        return self.name

    def begin(self) -> None:
        # This is called right as an animation is being
        # played.  As much initialization as possible,
        # especially any mobject copying, should live in
        # this method
        if self.time_span is not None:
            start, end = self.time_span
            self.run_time = max(end, self.run_time)
        self.mobject.set_animating_status(True)
        self.starting_mobject = self.create_starting_mobject()
        if self.suspend_mobject_updating:
            self.mobject_was_updating = not self.mobject.updating_suspended
            self.mobject.suspend_updating()
        self.families = list(self.get_all_families_zipped())
        self.interpolate(0)

    def finish(self) -> None:
        self.interpolate(self.final_alpha_value)
        self.mobject.set_animating_status(False)
        if self.suspend_mobject_updating and self.mobject_was_updating:
            self.mobject.resume_updating()

    def clean_up_from_scene(self, scene: Scene) -> None:
        if self.is_remover():
            scene.remove(self.mobject)

    def create_starting_mobject(self) -> Mobject:
        # Keep track of where the mobject starts
        return self.mobject.copy()

    def get_all_mobjects(self) -> tuple[Mobject, Mobject]:
        """
        Ordering must match the ording of arguments to interpolate_submobject
        """
        return self.mobject, self.starting_mobject

    def get_all_families_zipped(self) -> zip[tuple[Mobject]]:
        return zip(*[
            mob.get_family()
            for mob in self.get_all_mobjects()
        ])

    def update_mobjects(self, dt: float) -> None:
        """
        Updates things like starting_mobject, and (for
        Transforms) target_mobject.
        """
        for mob in self.get_all_mobjects_to_update():
            mob.update(dt)

    def get_all_mobjects_to_update(self) -> list[Mobject]:
        # The surrounding scene typically handles
        # updating of self.mobject.
        items = list(filter(
            lambda m: m is not self.mobject,
            self.get_all_mobjects()
        ))
        items = remove_list_redundancies(items)
        return items

    def copy(self):
        return deepcopy(self)

    def update_rate_info(
        self,
        run_time: float | None = None,
        rate_func: Callable[[float], float] | None = None,
        lag_ratio: float | None = None,
    ):
        self.run_time = run_time or self.run_time
        self.rate_func = rate_func or self.rate_func
        self.lag_ratio = lag_ratio or self.lag_ratio
        return self

    # Methods for interpolation, the mean of an Animation
    def interpolate(self, alpha: float) -> None:
        self.interpolate_mobject(alpha)

    def update(self, alpha: float) -> None:
        """
        This method shouldn't exist, but it's here to
        keep many old scenes from breaking
        """
        self.interpolate(alpha)

    def time_spanned_alpha(self, alpha: float) -> float:
        if self.time_span is not None:
            start, end = self.time_span
            return clip(alpha * self.run_time - start, 0, end - start) / (end - start)
        return alpha

    def interpolate_mobject(self, alpha: float) -> None:
        for i, mobs in enumerate(self.families):
            sub_alpha = self.get_sub_alpha(self.time_spanned_alpha(alpha), i, len(self.families))
            self.interpolate_submobject(*mobs, sub_alpha)

    def interpolate_submobject(
        self,
        submobject: Mobject,
        starting_submobject: Mobject,
        alpha: float
    ):
        # Typically ipmlemented by subclass
        pass

    def get_sub_alpha(
        self,
        alpha: float,
        index: int,
        num_submobjects: int
    ) -> float:
        # TODO, make this more understanable, and/or combine
        # its functionality with AnimationGroup's method
        # build_animations_with_timings
        lag_ratio = self.lag_ratio
        full_length = (num_submobjects - 1) * lag_ratio + 1
        value = alpha * full_length
        lower = index * lag_ratio
        raw_sub_alpha = clip((value - lower), 0, 1)
        return self.rate_func(raw_sub_alpha)

    # Getters and setters
    def set_run_time(self, run_time: float):
        self.run_time = run_time
        return self

    def get_run_time(self) -> float:
        if self.time_span:
            return max(self.run_time, self.time_span[1])
        return self.run_time

    def set_rate_func(self, rate_func: Callable[[float], float]):
        self.rate_func = rate_func
        return self

    def get_rate_func(self) -> Callable[[float], float]:
        return self.rate_func

    def set_name(self, name: str):
        self.name = name
        return self

    def is_remover(self) -> bool:
        return self.remover


def prepare_animation(anim: Animation | _AnimationBuilder):
    if isinstance(anim, _AnimationBuilder):
        return anim.build()

    if isinstance(anim, Animation):
        return anim

    raise TypeError(f"Object {anim} cannot be converted to an animation")
