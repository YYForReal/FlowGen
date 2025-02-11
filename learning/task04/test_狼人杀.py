##运行代码详情
#导入角色和游戏相关依赖
import asyncio
import fire

from metagpt.ext.werewolf.roles import Guard, Moderator, Seer, Villager, Werewolf, Witch # 守卫 主持人 先知 村民 狼人 巫师
from metagpt.ext.werewolf.roles.human_player import prepare_human_player
from metagpt.ext.werewolf.werewolf_game import WerewolfGame
from metagpt.logs import logger

#由于MetaGPT是异步框架，使用asyncio启动游戏
async def start_game(
    investment: float = 3.0,
    n_round: int = 5,#建议n_round值设置小一点
    shuffle: bool = True,
    add_human: bool = False,
    use_reflection: bool = True,
    use_experience: bool = False,
    use_memory_selection: bool = False,
    new_experience_version: str = "",
):
    game = WerewolfGame()
    # 初始化游戏设置
    game_setup, players = game.env.init_game_setup(
        role_uniq_objs=[Villager, Werewolf, Guard, Seer, Witch],#设置游戏玩家职业
        num_werewolf=2,
        num_villager=2,
        shuffle=shuffle,#是否打乱职业顺序，默认打乱
        add_human=add_human,#设置真人也参与游戏
        use_reflection=use_reflection,#是否让智能体对对局信息反思，默认开启
        use_experience=use_experience,#是否让智能体根据过去行为优化自身动作，默认关闭
        use_memory_selection=use_memory_selection,
        new_experience_version=new_experience_version,
        prepare_human_player=prepare_human_player,
    )
    logger.info(f"{game_setup}")

    players = [Moderator()] + players#主持人加入游戏
    game.hire(players)
    game.invest(investment)
    game.run_project(game_setup)#主持人广播游戏情况
    await game.run(n_round=n_round)


def main(
    investment: float = 20.0,
    n_round: int = 12, # 运行前建议将此处n_round修改小一点，否则对钱包不友好！！！
    shuffle: bool = True,
    add_human: bool = False,
    use_reflection: bool = True,
    use_experience: bool = False,
    use_memory_selection: bool = False,
    new_experience_version: str = "",
):
    asyncio.run(
        start_game(
            investment,
            n_round,
            shuffle,
            add_human,
            use_reflection,
            use_experience,
            use_memory_selection,
            new_experience_version,
        )
    )


if __name__ == "__main__":
    fire.Fire(main)