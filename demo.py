from agentic_system.workflow import run_requirement_workflow


if __name__ == "__main__":
    requirement = (
        "Build a reliable software service with clear user workflows, "
        "appropriate data handling, and a validation strategy."
    )
    result = run_requirement_workflow(requirement)
    print("Agentic workflow summary:")
    print(result["execution_summary"])
    print("\nArchitecture:")
    print(result["design"]) if "design" in result else print(result["architecture"])
