def generate_farm_analysis(
    location,
    farming_goal,
    farm_size,
    challenge
):

    recommendations = [
        f"Recommended farming strategy for {farming_goal}",
        f"Best practices for farming in {location}",
        "Use water-saving techniques",
        "Monitor soil health regularly"
    ]

    risks = [
        "Weather variability",
        "Pest infestations",
        "Input cost increases"
    ]

    resources_needed = [
        "Seeds",
        "Fertilizer",
        "Water source",
        "Basic farming tools"
    ]

    action_plan = [
        "Prepare land",
        "Acquire inputs",
        "Plant crops",
        "Monitor growth",
        "Harvest and sell"
    ]

    return {
        "recommendations": recommendations,
        "risks": risks,
        "resources_needed": resources_needed,
        "action_plan": action_plan
    }
