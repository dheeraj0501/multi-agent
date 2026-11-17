REQUIREMENTS = {
    "greenfield": "Build a new software service with clear workflows, appropriate persistence, and validation.",
    "brownfield": "Improve an existing software service's performance and observability without breaking its current API contracts.",
    "ambiguous": "Create a better internal tool so that the team can work faster and more reliably.",
}

if __name__ == "__main__":
    for name, requirement in REQUIREMENTS.items():
        print(f"{name}: {requirement}")
