"""
Example showing how to use tr-ai-cing to trace a LangGraph workflow.

This example demonstrates a simple LangGraph agent that:
1. Analyzes user input
2. Routes to appropriate handlers (search or direct response)
3. Generates a final response

The tr-ai-cing tracer captures all node executions and their relationships.
"""

from typing import Annotated, TypedDict, Literal
from tracing import Tracer, Visualizer


# Define the state that will be passed through the graph
class AgentState(TypedDict):
    """State passed between nodes in the graph."""
    messages: list[str]
    next_action: str
    final_response: str


def simulate_llm_call(prompt: str, model: str = "gpt-4") -> str:
    """Simulate an LLM call (replace with actual LLM API in production)."""
    # In a real implementation, this would call OpenAI, Anthropic, etc.
    if "search" in prompt.lower():
        return "search"
    elif "weather" in prompt.lower():
        return "The weather is sunny and 72°F"
    elif "capital" in prompt.lower():
        return "Paris is the capital of France"
    else:
        return f"I understand your message: {prompt}"


# Node functions for the graph
def analyze_input(state: AgentState, tracer: Tracer) -> AgentState:
    """Analyze the user input to determine the next action."""
    with tracer.span("analyze_input", span_type="agent_node"):
        user_message = state["messages"][-1]
        
        # Simulate LLM call to classify intent
        prompt = f"Classify the intent of this message: {user_message}"
        classification = simulate_llm_call(prompt)
        
        tracer.log_llm_call(
            name="intent_classification",
            input_data=prompt,
            output_data=classification,
            model="gpt-4",
            provider="openai",
            metadata={"node": "analyze_input"}
        )
        
        state["next_action"] = classification
        state["messages"].append(f"[Analysis: {classification}]")
        
    return state


def search_node(state: AgentState, tracer: Tracer) -> AgentState:
    """Execute a search and return results."""
    with tracer.span("search_node", span_type="agent_node"):
        user_message = state["messages"][0]
        
        # Simulate search operation
        prompt = f"Search for: {user_message}"
        search_results = f"Found information about: {user_message}"
        
        tracer.log_llm_call(
            name="search_execution",
            input_data=prompt,
            output_data=search_results,
            model="gpt-4",
            provider="openai",
            metadata={"node": "search_node", "search_type": "semantic"}
        )
        
        state["messages"].append(f"[Search results: {search_results}]")
        
    return state


def direct_response_node(state: AgentState, tracer: Tracer) -> AgentState:
    """Generate a direct response without search."""
    with tracer.span("direct_response_node", span_type="agent_node"):
        user_message = state["messages"][0]
        
        # Simulate direct LLM response
        prompt = f"Respond to: {user_message}"
        response = simulate_llm_call(prompt)
        
        tracer.log_llm_call(
            name="direct_response_generation",
            input_data=prompt,
            output_data=response,
            model="gpt-4",
            provider="openai",
            metadata={"node": "direct_response_node"}
        )
        
        state["messages"].append(f"[Direct response: {response}]")
        
    return state


def generate_final_response(state: AgentState, tracer: Tracer) -> AgentState:
    """Generate the final response based on all previous steps."""
    with tracer.span("generate_final_response", span_type="agent_node"):
        conversation_history = "\n".join(state["messages"])
        
        # Simulate final response generation
        prompt = f"Generate final response based on:\n{conversation_history}"
        final_response = simulate_llm_call(prompt)
        
        tracer.log_llm_call(
            name="final_response_synthesis",
            input_data=prompt,
            output_data=final_response,
            model="gpt-4",
            provider="openai",
            metadata={"node": "generate_final_response"}
        )
        
        state["final_response"] = final_response
        state["messages"].append(f"[Final: {final_response}]")
        
    return state


def route_after_analysis(state: AgentState) -> Literal["search", "direct_response"]:
    """Determine which node to execute next based on analysis."""
    if state["next_action"] == "search":
        return "search"
    else:
        return "direct_response"


def run_langgraph_workflow(user_input: str, tracer: Tracer):
    """
    Simulate a LangGraph workflow execution.
    
    In a real LangGraph implementation, you would use:
    - StateGraph to define the graph structure
    - add_node() to add nodes
    - add_edge() to connect nodes
    - add_conditional_edges() for routing
    - compile() to create the runnable graph
    
    This simplified version demonstrates the tracing pattern.
    """
    print(f"\n{'='*60}")
    print(f"Processing: {user_input}")
    print(f"{'='*60}\n")
    
    # Initialize state
    state: AgentState = {
        "messages": [user_input],
        "next_action": "",
        "final_response": ""
    }
    
    # Execute graph nodes in sequence (in real LangGraph, this is handled by the graph)
    with tracer.span("langgraph_workflow", span_type="workflow"):
        # Step 1: Analyze input
        state = analyze_input(state, tracer)
        print(f"✓ Analysis complete: {state['next_action']}")
        
        # Step 2: Route based on analysis
        next_step = route_after_analysis(state)
        print(f"✓ Routing to: {next_step}")
        
        # Step 3: Execute appropriate action
        if next_step == "search":
            state = search_node(state, tracer)
            print(f"✓ Search complete")
        else:
            state = direct_response_node(state, tracer)
            print(f"✓ Direct response generated")
        
        # Step 4: Generate final response
        state = generate_final_response(state, tracer)
        print(f"✓ Final response: {state['final_response']}\n")
    
    return state


def main():
    """Run multiple LangGraph workflow examples with tracing."""
    # Create tracer
    tracer = Tracer(log_file="examples/langgraph_trace.jsonl")
    
    # Start trace
    trace_id = tracer.start_trace()
    print(f"Started trace: {trace_id}")
    
    # Example 1: Question that should use search
    run_langgraph_workflow(
        "What's the weather like today?",
        tracer
    )
    
    # Example 2: Question that should get direct response
    run_langgraph_workflow(
        "What is the capital of France?",
        tracer
    )
    
    # Example 3: General query
    run_langgraph_workflow(
        "Tell me about artificial intelligence",
        tracer
    )
    
    # End trace
    tracer.end_trace()
    print(f"\n{'='*60}")
    print("Trace completed!")
    print(f"{'='*60}\n")
    
    # Generate visualization
    print("Generating visualization...")
    visualizer = Visualizer(log_file="examples/langgraph_trace.jsonl")
    output_file = visualizer.generate_html("examples/langgraph_visualization.html")
    print(f"Visualization saved to: {output_file}")
    print("Open the HTML file in your browser to see the graph execution trace!")
    print("\nThe visualization shows:")
    print("  - The workflow hierarchy (parent-child relationships)")
    print("  - Timing information for each node")
    print("  - Input/output data for each LLM call")
    print("  - The routing decisions made by the graph")


if __name__ == "__main__":
    main()
