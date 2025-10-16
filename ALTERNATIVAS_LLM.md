# 🤖 Alternativas de Modelos LLM

Esta guía explica cómo configurar diferentes proveedores de modelos de lenguaje para el microservicio.

## 🔄 Proveedores Soportados

### 1. Google Gemini (Actual)
- **Modelo**: gemini-pro
- **Ventajas**: Gratuito, rápido, buena calidad
- **Desventajas**: Limitaciones de rate limit

### 2. OpenAI GPT
- **Modelos**: gpt-3.5-turbo, gpt-4, gpt-4-turbo
- **Ventajas**: Excelente calidad, amplio contexto
- **Desventajas**: Costoso, requiere API key

### 3. Anthropic Claude
- **Modelos**: claude-3-sonnet, claude-3-opus
- **Ventajas**: Muy buena calidad, seguro
- **Desventajas**: Costoso, limitaciones de acceso

### 4. Azure OpenAI
- **Modelos**: gpt-3.5-turbo, gpt-4
- **Ventajas**: Enterprise-ready, compliance
- **Desventajas**: Configuración compleja

## 🔧 Configuración por Proveedor

### Google Gemini (Actual)
```bash
# .env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=AIzaSyAWRoXr18XDdpA8tALdmqBlH9zBMUNuNFw
GOOGLE_PROJECT_ID=494189632161
GEMINI_MODEL=gemini-pro
```

### OpenAI GPT
```bash
# .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_ORGANIZATION=org-your-org-id
```

### Anthropic Claude
```bash
# .env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-claude-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### Azure OpenAI
```bash
# .env
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## 🔄 Implementación de Múltiples Proveedores

### Modificar llm_wrapper.py

```python
import os
from typing import Dict, Any, Optional
import google.generativeai as genai
import openai
import anthropic
from azure.ai.openai import AzureOpenAI

class LLMWrapper:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "gemini")
        self._setup_provider()
    
    def _setup_provider(self):
        """Configurar proveedor específico"""
        if self.provider == "gemini":
            self._setup_gemini()
        elif self.provider == "openai":
            self._setup_openai()
        elif self.provider == "anthropic":
            self._setup_anthropic()
        elif self.provider == "azure":
            self._setup_azure()
        else:
            raise ValueError(f"Proveedor no soportado: {self.provider}")
    
    def _setup_gemini(self):
        """Configurar Google Gemini"""
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-pro")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY no configurado")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
    
    def _setup_openai(self):
        """Configurar OpenAI"""
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        organization = os.getenv("OPENAI_ORGANIZATION")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY no configurado")
        
        openai.api_key = api_key
        if organization:
            openai.organization = organization
        
        self.model_name = model_name
        self.client = openai.OpenAI(api_key=api_key, organization=organization)
    
    def _setup_anthropic(self):
        """Configurar Anthropic Claude"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no configurado")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model_name
    
    def _setup_azure(self):
        """Configurar Azure OpenAI"""
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not all([api_key, endpoint, deployment]):
            raise ValueError("Configuración de Azure OpenAI incompleta")
        
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )
        self.model_name = deployment
    
    async def _generate_response(self, prompt: str) -> str:
        """Generar respuesta usando el proveedor configurado"""
        if self.provider == "gemini":
            return await self._generate_gemini(prompt)
        elif self.provider == "openai":
            return await self._generate_openai(prompt)
        elif self.provider == "anthropic":
            return await self._generate_anthropic(prompt)
        elif self.provider == "azure":
            return await self._generate_azure(prompt)
        else:
            raise ValueError(f"Proveedor no soportado: {self.provider}")
    
    async def _generate_gemini(self, prompt: str) -> str:
        """Generar respuesta con Gemini"""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(prompt)
        )
        return response.text
    
    async def _generate_openai(self, prompt: str) -> str:
        """Generar respuesta con OpenAI"""
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=int(os.getenv("MAX_TOKENS", "2048")),
            temperature=float(os.getenv("TEMPERATURE", "0.7"))
        )
        return response.choices[0].message.content
    
    async def _generate_anthropic(self, prompt: str) -> str:
        """Generar respuesta con Claude"""
        response = await self.client.messages.create(
            model=self.model_name,
            max_tokens=int(os.getenv("MAX_TOKENS", "2048")),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    async def _generate_azure(self, prompt: str) -> str:
        """Generar respuesta con Azure OpenAI"""
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=int(os.getenv("MAX_TOKENS", "2048")),
            temperature=float(os.getenv("TEMPERATURE", "0.7"))
        )
        return response.choices[0].message.content
```

## 📊 Comparación de Proveedores

| Característica | Gemini | OpenAI | Claude | Azure |
|----------------|--------|--------|--------|-------|
| **Costo** | Gratuito | Medio-Alto | Alto | Medio-Alto |
| **Calidad** | Buena | Excelente | Excelente | Excelente |
| **Velocidad** | Rápida | Media | Media | Media |
| **Contexto** | 32K | 16K-128K | 200K | 16K-128K |
| **Disponibilidad** | Alta | Alta | Limitada | Alta |
| **Enterprise** | No | Sí | Sí | Sí |

## 🔄 Fallback y Load Balancing

### Implementar Fallback Automático
```python
class LLMWrapperWithFallback:
    def __init__(self):
        self.providers = self._setup_providers()
        self.current_provider = 0
    
    def _setup_providers(self):
        """Configurar múltiples proveedores"""
        providers = []
        
        # Gemini (principal)
        if os.getenv("GOOGLE_API_KEY"):
            providers.append({
                "name": "gemini",
                "setup": self._setup_gemini,
                "generate": self._generate_gemini
            })
        
        # OpenAI (fallback)
        if os.getenv("OPENAI_API_KEY"):
            providers.append({
                "name": "openai",
                "setup": self._setup_openai,
                "generate": self._generate_openai
            })
        
        return providers
    
    async def _generate_response_with_fallback(self, prompt: str) -> str:
        """Generar respuesta con fallback automático"""
        last_error = None
        
        for i, provider in enumerate(self.providers):
            try:
                return await provider["generate"](prompt)
            except Exception as e:
                logger.warning(f"Proveedor {provider['name']} falló: {e}")
                last_error = e
                continue
        
        raise Exception(f"Todos los proveedores fallaron. Último error: {last_error}")
```

## 🧪 Testing con Diferentes Proveedores

### Test de Proveedores
```python
# tests/test_llm_providers.py
import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.parametrize("provider", ["gemini", "openai", "anthropic", "azure"])
async def test_provider_generation(provider):
    """Test generación con diferentes proveedores"""
    with patch.dict('os.environ', {
        f'{provider.upper()}_API_KEY': 'test-key',
        'LLM_PROVIDER': provider
    }):
        wrapper = LLMWrapper()
        response = await wrapper._generate_response("Test prompt")
        assert response is not None
        assert len(response) > 0
```

## 💰 Optimización de Costos

### Estrategias de Costo
1. **Usar modelos más baratos para tareas simples**
2. **Implementar cache de respuestas**
3. **Batch processing para múltiples requests**
4. **Rate limiting inteligente**

### Cache de Respuestas
```python
import redis
import json
import hashlib

class CachedLLMWrapper(LLMWrapper):
    def __init__(self):
        super().__init__()
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379")
        )
        self.cache_ttl = int(os.getenv("CACHE_TTL", "3600"))
    
    async def _generate_response(self, prompt: str) -> str:
        # Generar hash del prompt
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        cache_key = f"llm_response:{prompt_hash}"
        
        # Intentar obtener del cache
        cached_response = self.redis_client.get(cache_key)
        if cached_response:
            logger.info("Respuesta obtenida del cache")
            return json.loads(cached_response)
        
        # Generar nueva respuesta
        response = await super()._generate_response(prompt)
        
        # Guardar en cache
        self.redis_client.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(response)
        )
        
        return response
```

## 🔧 Configuración de Producción

### Variables de Entorno por Ambiente

#### Desarrollo
```bash
# .env.development
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-dev-key
GEMINI_MODEL=gemini-pro
MAX_TOKENS=1024
TEMPERATURE=0.7
```

#### Producción
```bash
# .env.production
LLM_PROVIDER=openai
OPENAI_API_KEY=your-prod-key
OPENAI_MODEL=gpt-4
MAX_TOKENS=2048
TEMPERATURE=0.3
CACHE_ENABLED=true
CACHE_TTL=3600
```

### Monitoreo de Costos
```python
# En llm_wrapper.py
class CostTrackingLLMWrapper(LLMWrapper):
    def __init__(self):
        super().__init__()
        self.cost_tracker = {}
    
    async def _generate_response(self, prompt: str) -> str:
        start_time = time.time()
        response = await super()._generate_response(prompt)
        end_time = time.time()
        
        # Calcular costo (simplificado)
        cost = self._calculate_cost(prompt, response, end_time - start_time)
        self._track_cost(cost)
        
        return response
    
    def _calculate_cost(self, prompt: str, response: str, duration: float) -> float:
        """Calcular costo basado en tokens y tiempo"""
        prompt_tokens = len(prompt.split())
        response_tokens = len(response.split())
        
        # Precios aproximados por 1K tokens
        pricing = {
            "gemini": {"input": 0.0, "output": 0.0},  # Gratuito
            "openai": {"input": 0.0015, "output": 0.002},
            "anthropic": {"input": 0.003, "output": 0.015},
            "azure": {"input": 0.0015, "output": 0.002}
        }
        
        provider_pricing = pricing.get(self.provider, {"input": 0.001, "output": 0.002})
        
        input_cost = (prompt_tokens / 1000) * provider_pricing["input"]
        output_cost = (response_tokens / 1000) * provider_pricing["output"]
        
        return input_cost + output_cost
```

Esta configuración te permite usar cualquier proveedor de LLM de manera transparente, con fallback automático y optimización de costos.
