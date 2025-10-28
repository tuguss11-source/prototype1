# Ana Program - Bölüm 5 (Son)
$mainPart5 = @'

    async def shutdown(self):
        """Programı kapat"""
        logger.info("Shutting down trade program...")
        
        # WebSocket bağlantısını kapat
        await self.realtime_collector.stop()
        
        # Açık pozisyonları kapat (isteğe bağlı)
        # await self.close_all_positions()
        
        logger.info("Trade program shut down successfully")

async def main():
    """Ana fonksiyon"""
    program = TradeProgram()
    await program.run()

if __name__ == "__main__":
    asyncio.run(main())
'@

Add-Content -Path "main.py" -Value $mainPart5 -Encoding UTF8
Write-Host "✓ Ana program tamamlandı" -ForegroundColor Green