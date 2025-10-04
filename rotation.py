# 启用Python 3.7+的注解向前兼容支持，允许在类型注解中使用尚未定义的类
from __future__ import annotations

# 从Manim的动画模块导入基础动画类
from manimlib.animation.animation import Animation

# 从常量模块导入常用的空间坐标和方向常量
# ORIGIN：原点坐标 (0, 0, 0)
# OUT：垂直于屏幕向外的方向向量
from manimlib.constants import ORIGIN, OUT

# 导入数学常量：PI(π)和TAU(τ=2π)
from manimlib.constants import PI, TAU

# 从速率函数工具模块导入常用的速率函数
# linear：线性速率函数（匀速）
# smooth：平滑速率函数（缓进缓出）
from manimlib.utils.rate_functions import linear, smooth

# 导入类型检查相关模块
from typing import TYPE_CHECKING

# 条件导入，仅在类型检查时执行（运行时不执行）
# 用于解决循环导入问题，同时提供完整的类型提示
if TYPE_CHECKING:
    import numpy as np
    from typing import Callable
    from manimlib.mobject.mobject import Mobject


class Rotating(Animation):
    def __init__(
        self,
        mobject: Mobject,
        angle: float = TAU,
        axis: np.ndarray = OUT,
        about_point: np.ndarray | None = None,
        about_edge: np.ndarray | None = None,
        run_time: float = 5.0,
        rate_func: Callable[[float], float] = linear,
        suspend_mobject_updating: bool = False,
        **kwargs
    ):
        self.angle = angle
        self.axis = axis
        self.about_point = about_point
        self.about_edge = about_edge
        super().__init__(
            mobject,
            run_time=run_time,
            rate_func=rate_func,
            suspend_mobject_updating=suspend_mobject_updating,
            **kwargs
        )

    def interpolate_mobject(self, alpha: float) -> None:
        pairs = zip(
            self.mobject.family_members_with_points(),
            self.starting_mobject.family_members_with_points(),
        )
        for sm1, sm2 in pairs:
            for key in sm1.pointlike_data_keys:
                sm1.data[key][:] = sm2.data[key]
        self.mobject.rotate(
            self.rate_func(self.time_spanned_alpha(alpha)) * self.angle,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )


class Rotate(Rotating):
    def __init__(
        self,
        mobject: Mobject,
        angle: float = PI,
        axis: np.ndarray = OUT,
        run_time: float = 1,
        rate_func: Callable[[float], float] = smooth,
        about_edge: np.ndarray = ORIGIN,
        **kwargs
    ):
        super().__init__(
            mobject, angle, axis,
            run_time=run_time,
            rate_func=rate_func,
            about_edge=about_edge,
            **kwargs
        )
