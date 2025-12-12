from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from mcp.server.fastmcp import FastMCP  # Utilizando o servidor rápido do MCP

# --- 1. Configuração Inicial ---
app = FastAPI(title="Agendar Serviço")
mcp_server = FastMCP("SchedulingAI")

# --- 2. Simulação de Banco de Dados (Mock) ---
# Em produção, isso viria do PostgreSQL
SERVICES = {
    1: "Corte de Cabelo (30 min)",
    2: "Manicure (45 min)"
}

# Lista de horários já ocupados (exemplo)
BUSY_SCHEDULES = [
    {"data": "2025-10-20", "hora": "14:00"},
    {"data": "2025-10-20", "hora": "15:00"}
]


# --- 3. Schemas (Pydantic) ---
# Isso é crucial: define o formato de dados para a API e para a IA
class CheckAvailability(BaseModel):
    date: str = Field(..., description="Data no formato YYYY-MM-DD")
    hour: str = Field(..., description="Hora no formato HH:MM")


# --- 4. Lógica de Negócio Central ---
def _check_logic(date: str, hour: str) -> bool:
    """Retorna True se estiver livre, False se estiver ocupado."""
    for scheduling in BUSY_SCHEDULES:
        if scheduling["date"] == date and scheduling["hour"] == hour:
            return False  # Ocupado
    return True  # Livre


# --- 5. Exposição para o FRONTEND (API REST) ---
@app.post("/api/check-availability")
async def api_to_check(data: CheckAvailability):
    free_time = _check_logic(data.date, data.hour)
    if not free_time:
        return {"status": "ocupado", "mensagem": "Horário indisponível."}
    return {"status": "livre", "mensagem": "Horário disponível para agendamento."}


# --- 6. Exposição para o AGENTE DE IA (MCP Tool) ---
@mcp_server.tool()
def check_schedule_availability(date: str, hour: str) -> str:
    """
    Verifica se existe disponibilidade para agendar um serviço em uma data e hora específicas.
    Use esta ferramenta antes de tentar realizar qualquer agendamento.
    """
    free_time = _check_logic(date, hour)

    if free_time:
        return f"DISPONÍVEL: O horário das {hour} no dia {date} está livre."
    else:
        return f"INDISPONÍVEL: O horário das {hour} no dia {date} já está ocupado. Sugira outro horário."


# Para rodar o servidor MCP (separadamente do Uvicorn se necessário)
if __name__ == "__main__":
    mcp_server.run()