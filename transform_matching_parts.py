# 从__future__模块导入annotations，支持类型注释的延迟评估
# 允许在类型提示中使用尚未定义的类或函数
from __future__ import annotations

# 导入itertools模块并简写为it，用于创建迭代器和处理迭代相关操作
import itertools as it
# 从difflib模块导入SequenceMatcher，用于字符串序列的相似性比较
from difflib import SequenceMatcher

# 从manimlib.animation.composition导入AnimationGroup
# AnimationGroup用于将多个动画组合在一起同时或按顺序播放
from manimlib.animation.composition import AnimationGroup
# 从manimlib.animation.fading导入FadeInFromPoint
# FadeInFromPoint是从指定点淡入的动画效果
from manimlib.animation.fading import FadeInFromPoint
# 从manimlib.animation.fading导入FadeOutToPoint
# FadeOutToPoint是向指定点淡出的动画效果
from manimlib.animation.transform import Transform
# 从manimlib.mobject.mobject导入Mobject
# Mobject是所有可移动对象的基类
from manimlib.mobject.mobject import Mobject
# 从manimlib.mobject.types.vectorized_mobject导入VMobject
# VMobject是向量图形对象的基类，支持更复杂的图形操作
from manimlib.mobject.svg.string_mobject import StringMobject
# StringMobject用于处理字符串的可移动对象

# 从typing模块导入TYPE_CHECKING常量
# 用于在类型检查阶段执行特定代码，运行时不执行
from typing import TYPE_CHECKING

# 条件判断：仅在类型检查时执行以下代码块
if TYPE_CHECKING:
    # 从typing模块导入Iterable类型，用于标注可迭代对象
    from typing import Iterable
    # 从manimlib.scene.scene导入Scene类
    # Scene是所有场景的基类，用于组织和播放动画
    from manimlib.scene.scene import Scene


# 定义TransformMatchingParts类，继承自AnimationGroup，用于创建匹配部分变换的动画组
class TransformMatchingParts(AnimationGroup):
    def __init__(
        self,
        source: Mobject,  # 源对象，动画的起始对象
        target: Mobject,  # 目标对象，动画的结束对象
        matched_pairs: Iterable[tuple[Mobject, Mobject]] = [],  # 预定义的匹配对列表
        match_animation: type = Transform,  # 用于匹配部分的动画类型
        mismatch_animation: type = Transform,  # 用于不匹配部分的动画类型
        run_time: float = 2,  # 动画总时长
        lag_ratio: float = 0,  # 动画组中各子动画的延迟比例
        **kwargs,  # 传递给动画的其他参数
    ):
        # 保存源对象和目标对象
        self.source = source
        self.target = target
        # 保存匹配和不匹配部分使用的动画类型
        self.match_animation = match_animation
        self.mismatch_animation = mismatch_animation
        # 保存动画配置参数
        self.anim_config = dict(** kwargs)

        # 逐步构建从源对象部分到目标对象部分的变换列表
        # 这两个列表跟踪到目前为止已处理的部分
        # 获取源对象和目标对象中所有带有点的子对象
        self.source_pieces = source.family_members_with_points()
        self.target_pieces = target.family_members_with_points()
        # 存储所有动画的列表
        self.anims = []

        # 处理预定义的匹配对
        for pair in matched_pairs:
            self.add_transform(*pair)

        # 匹配任何具有相同形状的对
        for pair in self.find_pairs_with_matching_shapes(self.source_pieces, self.target_pieces):
            self.add_transform(*pair)

        # 最后，处理不匹配的部分
        # 处理源对象中未匹配的部分：淡出到目标对象中心
        for source_piece in self.source_pieces:
            # 检查该源对象部分是否已在动画中
            if any([source_piece in anim.mobject.get_family() for anim in self.anims]):
                continue
            # 添加淡出动画
            self.anims.append(FadeOutToPoint(
                source_piece, target.get_center(),
                **self.anim_config
            ))
        # 处理目标对象中未匹配的部分：从源对象中心淡入
        for target_piece in self.target_pieces:
            # 检查该目标对象部分是否已在动画中
            if any([target_piece in anim.mobject.get_family() for anim in self.anims]):
                continue
            # 添加淡入动画
            self.anims.append(FadeInFromPoint(
                target_piece, source.get_center(),
                **self.anim_config
            ))

        # 调用父类AnimationGroup的初始化方法
        super().__init__(
            *self.anims,  # 展开所有动画
            run_time=run_time,  # 动画总时长
            lag_ratio=lag_ratio,  # 延迟比例
        )

    def add_transform(
        self,
        source: Mobject,  # 源部分对象
        target: Mobject,  # 目标部分对象
    ):
        # 获取源部分和目标部分中所有带有点的子对象
        new_source_pieces = source.family_members_with_points()
        new_target_pieces = target.family_members_with_points()
        # 如果源部分或目标部分为空，则不创建动画
        if len(new_source_pieces) == 0 or len(new_target_pieces) == 0:
            return
        # 检查源部分和目标部分是否都是未处理的新部分
        source_is_new = all(char in self.source_pieces for char in new_source_pieces)
        target_is_new = all(char in self.target_pieces for char in new_target_pieces)
        if not source_is_new or not target_is_new:
            return

        # 根据形状是否匹配选择动画类型
        transform_type = self.mismatch_animation 
        if source.has_same_shape_as(target):
            transform_type = self.match_animation

        # 添加变换动画
        self.anims.append(transform_type(source, target, **self.anim_config))
        # 从待处理列表中移除已匹配的部分
        for char in new_source_pieces:
            self.source_pieces.remove(char)
        for char in new_target_pieces:
            self.target_pieces.remove(char)

    def find_pairs_with_matching_shapes(
        self,
        chars1: list[Mobject],  # 第一组对象
        chars2: list[Mobject]  # 第二组对象
    ) -> list[tuple[Mobject, Mobject]]:
        """查找具有相同形状的对象对"""
        result = []
        # 遍历所有可能的组合
        for char1, char2 in it.product(chars1, chars2):
            # 检查形状是否相同
            if char1.has_same_shape_as(char2):
                result.append((char1, char2))
        return result

    def clean_up_from_scene(self, scene: Scene) -> None:
        """从场景中清理动画对象"""
        # 调用父类的清理方法
        super().clean_up_from_scene(scene)
        # 从场景中移除源对象
        scene.remove(self.mobject)
        # 将目标对象添加到场景中
        scene.add(self.target)


# 定义TransformMatchingShapes类，继承自TransformMatchingParts
# 这是TransformMatchingParts类的一个别名，功能完全相同
class TransformMatchingShapes(TransformMatchingParts):
    """Alias for TransformMatchingParts"""
    pass  # 不添加任何新功能，仅作为别名存在


class TransformMatchingStrings(TransformMatchingParts):
    """
    继承自TransformMatchingParts类，专门用于字符串之间的变换动画
    能够智能匹配源字符串和目标字符串中相同的部分，实现平滑过渡
    """
    def __init__(
        self,
        source: StringMobject,  # 源字符串对象
        target: StringMobject,  # 目标字符串对象
        matched_keys: Iterable[str] = [],  # 用户指定的要匹配的字符串键（子串）
        key_map: dict[str, str] = dict(),  # 字符串键映射，{源子串: 目标子串}
        matched_pairs: Iterable[tuple[VMobject, VMobject]] = [],  # 预定义的匹配对象对
        **kwargs,  # 传递给父类的其他参数
    ):
        # 组合所有匹配对：预定义的匹配对 + 自动匹配的字符串块
        matched_pairs = [
            *matched_pairs,  # 展开预定义的匹配对
            # 自动查找并添加匹配的字符串块
            *self.matching_blocks(source, target, matched_keys, key_map),
        ]

        # 调用父类TransformMatchingParts的初始化方法
        super().__init__(
            source, target,
            matched_pairs=matched_pairs,** kwargs,
        )

    def matching_blocks(
        self,
        source: StringMobject,
        target: StringMobject,
        matched_keys: Iterable[str],
        key_map: dict[str, str]
    ) -> list[tuple[VMobject, VMobject]]:
        """
        查找源字符串和目标字符串中匹配的子串块，返回对应的对象对
        
        参数:
            source: 源字符串对象
            target: 目标字符串对象
            matched_keys: 用户指定的匹配键
            key_map: 键映射关系
        
        返回:
            匹配的子串对象对列表
        """
        # 获取源字符串和目标字符串的符号子串列表
        syms1 = source.get_symbol_substrings()
        syms2 = target.get_symbol_substrings()
        
        # 获取每个子串对应的路径数量（用于索引计算）
        counts1 = list(map(source.substr_to_path_count, syms1))
        counts2 = list(map(target.substr_to_path_count, syms2))

        # 先处理用户指定的匹配
        # 添加matched_keys中指定的子串匹配对
        blocks = [(source[key], target[key]) for key in matched_keys]
        # 添加key_map中指定的子串映射对
        blocks += [(source[key1], target[key2]) for key1, key2 in key_map.items()]

        # 将已匹配的部分标记为"Null"，避免重复匹配
        for sub_source, sub_target in blocks:
            # 处理源字符串中已匹配的部分
            for i in range(len(syms1)):
                if source[i] in sub_source.family_members_with_points():
                    syms1[i] = "Null1"
            # 处理目标字符串中已匹配的部分
            for j in range(len(syms2)):
                if target[j] in sub_target.family_members_with_points():
                    syms2[j] = "Null2"

        # 自动查找最长的匹配子串并分组
        while True:
            # 创建序列匹配器，比较两个符号列表
            matcher = SequenceMatcher(None, syms1, syms2)
            # 查找最长的匹配子序列
            match = matcher.find_longest_match(0, len(syms1), 0, len(syms2))
            # 如果没有找到匹配的子序列，退出循环
            if match.size == 0:
                break

            # 计算源字符串中匹配块的起始索引和大小
            i1 = sum(counts1[:match.a])
            size = sum(counts1[match.a:match.a + match.size])
            # 计算目标字符串中匹配块的起始索引
            i2 = sum(counts2[:match.b])

            # 添加匹配块的对象对
            blocks.append((source[i1:i1 + size], target[i2:i2 + size]))

            # 将已匹配的部分标记为"Null"，避免重复匹配
            for i in range(match.size):
                syms1[match.a + i] = "Null1"
                syms2[match.b + i] = "Null2"

        # 返回所有匹配的对象对
        return blocks


# 定义TransformMatchingTex类，继承自TransformMatchingStrings
# 这是TransformMatchingStrings类的一个别名，功能完全相同
class TransformMatchingTex(TransformMatchingStrings):
    """Alias for TransformMatchingStrings"""
    pass  # 不添加任何新功能，仅作为别名存在
