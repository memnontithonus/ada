from ADA.ADA_Local import ADA
import asyncio

async def main():
    ada = ADA()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(ada.listen())
        input_message = tg.create_task(ada.input_message())
        tg.create_task(ada.send_prompt())
        tg.create_task(ada.text_to_speech())

        await input_message

if __name__ == "__main__":
    asyncio.run(main())