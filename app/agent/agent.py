"""
agent.py — High-level ClinicLeadAgent class.

This is the main interface your teammates call.
Usage:
    from app.agent.agent import ClinicLeadAgent
    from app.schemas.request import ClinicSearchRequest

    agent = ClinicLeadAgent()
    response = agent.run(ClinicSearchRequest(locations=["London"], clinic_types=["Dental Clinic"]))
"""
from app.graph.graph import clinic_graph
from app.graph.state import AgentState
from app.schemas.request import ClinicSearchRequest
from app.schemas.response import AgentResponse
from app.agent.memory import AgentMemory
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ClinicLeadAgent:
    """
    Orchestrates the full clinic lead generation workflow via LangGraph.

    Parameters
    ----------
    memory : AgentMemory, optional
        Pass an existing memory object to continue a multi-turn conversation.
    """

    def __init__(self, memory: AgentMemory = None):
        self.memory = memory or AgentMemory()
        self.graph = clinic_graph

    def run(self, request: ClinicSearchRequest) -> AgentResponse:
        """
        Execute a full lead-generation run.

        Parameters
        ----------
        request : ClinicSearchRequest
            User-provided search parameters.

        Returns
        -------
        AgentResponse
            Validated leads plus metadata and summary.
        """
        logger.info(
            "ClinicLeadAgent.run() called | locations=%s | types=%s | max=%d",
            request.locations,
            request.clinic_types,
            request.max_results,
        )

        # Store user request in memory for multi-turn context
        self.memory.add_user_message(
            f"Find {request.max_results} clinic leads in: {request.locations} "
            f"for types: {request.clinic_types}"
        )

        # Build initial state
        initial_state = AgentState(request=request)

        try:
            # Run the LangGraph workflow
            # LangGraph returns a plain dict, not an AgentState object
            final_state: dict = self.graph.invoke(initial_state)

            summary = final_state.get("summary", "")
            leads = final_state.get("validated_leads", [])
            errors = final_state.get("errors", [])
            run_id = final_state.get("run_id")

            # Record agent response in memory
            self.memory.add_ai_message(summary)

            response = AgentResponse(
                success=True,
                total_found=len(leads),
                leads=leads,
                summary=summary,
                errors=errors,
                run_id=run_id,
            )
            logger.info(
                "Run [%s] finished: %d leads | %d errors",
                response.run_id,
                response.total_found,
                len(response.errors),
            )
            return response

        except Exception as e:
            logger.error("Agent run failed: %s", e, exc_info=True)
            return AgentResponse(
                success=False,
                errors=[str(e)],
                summary=f"Run failed: {e}",
            )

    def chat(self, user_message: str, base_request: ClinicSearchRequest = None) -> str:
        """
        Conversational interface — useful for follow-up queries like
        'Now also search in Dubai' or 'Filter to only Manual clinics'.

        Parameters
        ----------
        user_message : str
            Natural language follow-up from the user.
        base_request : ClinicSearchRequest, optional
            Starting request to modify based on the message.

        Returns
        -------
        str
            Agent's response message.
        """
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage
        from app.agent.prompts import SYSTEM_PROMPT
        from config import config

        llm = ChatOpenAI(model=config.OPENAI_MODEL, api_key=config.OPENAI_API_KEY)

        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        messages += [
            HumanMessage(content=m["content"]) if m["role"] == "user"
            else SystemMessage(content=m["content"])
            for m in self.memory.to_dict_list()
        ]
        messages.append(HumanMessage(content=user_message))

        response = llm.invoke(messages)
        self.memory.add_user_message(user_message)
        self.memory.add_ai_message(response.content)
        return response.content
