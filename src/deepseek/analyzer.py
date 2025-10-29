import requests
import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class DeepSeekAnalyzer:
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None, local_mode: bool = False):
        self.logger = self._setup_logger()
        self.local_mode = local_mode
        
        if self.local_mode:
            # Local LM Studio modu
            self.base_url = base_url or "http://localhost:1234/v1"
            self.model = model or self._detect_available_model()
            self.headers = {
                "Content-Type": "application/json"
            }
        else:
            # Cloud DeepSeek API modu
            self.api_key = api_key
            self.base_url = base_url or "https://api.deepseek.com/v1"
            self.model = model or "deepseek-chat"
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}" if api_key else ""
            }
        
    def _setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/deepseek_analysis.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _detect_available_model(self) -> str:
        """
        LM Studio'da mevcut modelleri tespit et
        """
        try:
            response = requests.get(f"{self.base_url}/models", timeout=10)
            if response.status_code == 200:
                models = response.json().get("data", [])
                for model in models:
                    model_id = model.get("id", "").lower()
                    if "deepseek" in model_id:
                        return model.get("id")
                    elif "qwen" in model_id:
                        return model.get("id")
                
                # Hiçbiri yoksa ilk modeli kullan
                if models:
                    return models[0].get("id")
        except:
            pass
        
        # Varsayılan model
        return "deepseek-coder"
    
    def analyze_trading_signals(self, symbol: str, strategies_results: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """
        DeepSeek ile analiz - local veya cloud
        """
        try:
            if self.local_mode:
                if not self.test_connection():
                    raise ConnectionError("LM Studio bağlantısı yok. Lütfen LM Studio'yu çalıştırın.")
                prompt = self._create_local_analysis_prompt(symbol, strategies_results, current_price)
                response = self._query_local_deepseek(prompt)
                source = f"LOCAL_DEEPSEEK ({self.model})"
            else:
                if not self.api_key:
                    raise ValueError("DeepSeek API key gereklidir")
                prompt = self._create_analysis_prompt(symbol, strategies_results, current_price)
                response = self._query_deepseek_api(prompt)
                source = "DEEPSEEK_API"
            
            analysis = self._parse_response(response)
            
            return {
                "symbol": symbol,
                "analysis": analysis,
                "timestamp": datetime.now(),
                "recommendation": analysis.get("recommendation", "BEKLE"),
                "confidence": analysis.get("confidence", 0),
                "reasoning": analysis.get("reasoning", "Analiz yapılamadı"),
                "risk_level": analysis.get("risk_level", "ORTA"),
                "market_context": analysis.get("market_context", ""),
                "price_targets": analysis.get("price_targets", {}),
                "source": source
            }
            
        except Exception as e:
            self.logger.error(f"DeepSeek analiz hatası ({symbol}): {e}")
            raise ConnectionError(f"DeepSeek analiz hatası: {e}")
    
    def _create_analysis_prompt(self, symbol: str, strategies_results: Dict[str, Any], current_price: float) -> str:
        """
        Cloud analiz için prompt
        """
        prompt = f"""
        KRİPTO TRADING ANALİZİ - {symbol}
        
        MEVCUT FİYAT: ${current_price}
        
        TEKNİK ANALİZ SONUÇLARI:
        - Scalp Stratejisi: {strategies_results['scalp']['signal']} (%{strategies_results['scalp']['confidence']*100:.1f} güven)
        - Swing Stratejisi: {strategies_results['swing']['signal']} (%{strategies_results['swing']['confidence']*100:.1f} güven)
        - Günlük Strateji: {strategies_results['daily']['signal']} (%{strategies_results['daily']['confidence']*100:.1f} güven)
        
        Lütfen aşağıdaki JSON formatında kapsamlı bir analiz sağla:
        {{
            "recommendation": "AL/SAT/BEKLE",
            "confidence": 75,
            "risk_level": "DÜŞÜK/ORTA/YÜKSEK",
            "reasoning": "Detaylı analiz ve gerekçe...",
            "market_context": "Genel piyasa durumu değerlendirmesi...",
            "price_targets": {{
                "short_term": "hedef fiyat",
                "medium_term": "hedef fiyat", 
                "stop_loss": "stop loss fiyatı"
            }}
        }}
        
        Analiz kısa, net ve işe yarar bilgiler içermeli.
        """
        return prompt

    def _create_local_analysis_prompt(self, symbol: str, strategies_results: Dict[str, Any], current_price: float) -> str:
        """
        Local analiz için optimize edilmiş prompt
        """
        prompt = f"""
        KRİPTO TRADING ANALİZİ - {symbol}
        
        MEVCUT FİYAT: ${current_price}
        
        TEKNİK ANALİZ SONUÇLARI:
        - Scalp: {strategies_results['scalp']['signal']} (%{strategies_results['scalp']['confidence']*100:.1f})
        - Swing: {strategies_results['swing']['signal']} (%{strategies_results['swing']['confidence']*100:.1f})
        - Daily: {strategies_results['daily']['signal']} (%{strategies_results['daily']['confidence']*100:.1f})
        
        Lütfen kısa ve net bir şekilde JSON formatında analiz sağla:
        {{
            "recommendation": "AL/SAT/BEKLE",
            "confidence": 75,
            "risk_level": "DÜŞÜK/ORTA/YÜKSEK",
            "reasoning": "Kısa analiz ve gerekçe",
            "market_context": "Piyasa durumu"
        }}
        """
        return prompt
    
    def _query_deepseek_api(self, prompt: str) -> str:
        """
        Cloud DeepSeek API'ye sorgu gönder
        """
        try:
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Sen bir finansal analiz uzmanısın. Kripto para trading sinyallerini analiz ediyorsun. Yanıtlarını her zaman JSON formatında ver."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1000,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = f"DeepSeek API hatası: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise ConnectionError(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "DeepSeek API zaman aşımı"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "DeepSeek API bağlantı hatası"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg)
        except Exception as e:
            error_msg = f"DeepSeek API sorgu hatası: {e}"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg)

    def _query_local_deepseek(self, prompt: str) -> str:
        """
        Local LM Studio'ya sorgu gönder
        """
        try:
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1000,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=120  # Local model için daha uzun timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = f"LM Studio API hatası: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise ConnectionError(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "LM Studio zaman aşımı - Model yanıt vermiyor"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "LM Studio bağlantı hatası - LM Studio çalışıyor mu?"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg)
        except Exception as e:
            error_msg = f"LM Studio sorgu hatası: {e}"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg)
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        API yanıtını ayrıştır
        """
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start == -1 or end == 0:
                raise ValueError("Geçerli JSON yanıtı alınamadı")
                
            json_str = response[start:end]
            return json.loads(json_str)
            
        except Exception as e:
            error_msg = f"Yanıt ayrıştırma hatası: {e}"
            self.logger.error(error_msg)
            # Basit bir fallback analiz döndür
            return {
                "recommendation": "BEKLE",
                "confidence": 50,
                "risk_level": "ORTA",
                "reasoning": "Analiz tamamlanamadı",
                "market_context": "Model yanıtı işlenemedi"
            }
    
    def test_connection(self) -> bool:
        """
        Bağlantıyı test et (local veya cloud)
        """
        try:
            if self.local_mode:
                response = requests.get(f"{self.base_url}/models", timeout=15)
                return response.status_code == 200
            else:
                if not self.api_key:
                    return False
                    
                data = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 5
                }
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=data,
                    timeout=10
                )
                return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        """
        Kullanılabilir modelleri listele (sadece local modda)
        """
        if not self.local_mode:
            return []
            
        try:
            response = requests.get(f"{self.base_url}/models", timeout=10)
            if response.status_code == 200:
                models = response.json().get("data", [])
                return [model.get("id", "Unknown") for model in models]
        except:
            pass
        return []