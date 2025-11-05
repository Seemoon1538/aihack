# main.py — v15.5.2 — ПОЛНЫЙ, СТАБИЛЬНЫЙ
import asyncio
import argparse
import yaml
from src.core.dispatcher import AttackDispatcher
from src.core.logger import RealTimeLogger
from src.ai.brain import NeuralBrain
from src.core.report import NeuralAutopsy

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--lhost")
    parser.add_argument("--lport", type=int)
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    logger = RealTimeLogger()
    logger.info("НЕЙРОННЫЙ ЛОГЕР v10.1 \n                  АКТИВИРОВАН")

    # ФИКС: NeuralBrain принимает ТОЛЬКО config
    brain = NeuralBrain(config)
    brain.restore()

    options = {
        "lhost": args.lhost,
        "lport": args.lport,
        "dump": True,
        "auth_token": None
    }

    dispatcher = AttackDispatcher(config, logger, brain)
    target = args.target.rstrip("/")

    logger.critical(f"БРЕШЬ: ЦЕЛЬ: \n                  {target}")
    if args.lhost and args.lport:
        logger.critical(f"БРЕШЬ: LHOST: \n                  {args.lhost}:{args.lport}")

    try:
        results = await dispatcher.execute_chain(target, options)
    except Exception as e:
        logger.error(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        results = []

    # ФИКС: ПЕРЕДАЁМ logger
    autopsy = NeuralAutopsy(results, target, config, logger)
    autopsy.generate()

if __name__ == "__main__":
    asyncio.run(main())