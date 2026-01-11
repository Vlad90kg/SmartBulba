class TapoBulb:
    def __init__(self, bulb):
        self.bulb = bulb

    async def on(self, brightness):
        await self.bulb.set_brightness(brightness)
        await self.bulb.turn_on()

    async def off(self):
        await self.bulb.turn_off()
