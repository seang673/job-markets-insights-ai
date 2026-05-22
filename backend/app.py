import gradio as gr
import requests
import plotly.express as px

API = "http://localhost:8000"

def load_insights(role):
    res = requests.get(f"{API}/api/insights/overview?role={role}").json()
    print("Insights Overview:", res)  # Debugging statement

    # Build charts
    skills_fig = px.bar(
        res["top_skills"],
        x="count",
        y="name",
        orientation="h",
        title="Top Skills"
    )

    tech_fig = px.bar(
        res["top_tech_stack"],
        x="count",
        y="name",
        orientation="h",
        title="Top Tech Stack"
    )

    seniority_fig = px.pie(
        res["seniority_distribution"],
        names="level",
        values="count",
        title="Seniority Distribution"
    )

    summary = f"**Total Jobs:** {res['total_jobs']}  \n**Role:** {res['role']}"

    return summary, skills_fig, tech_fig, seniority_fig

def scrape_and_refresh(role):
    # Trigger scraping
    requests.post(f"{API}/api/scrape?role={role}")

    # After scraping, fetch updated insights
    return load_insights(role)

with gr.Blocks() as demo:
    gr.Markdown("# Job Market Insights")

    with gr.Row():
        role = gr.Dropdown(
            ["Software Engineer",
             "Data Scientist",
             "Machine Learning Engineer",
             "Quality Assurance Engineer",
             "Backend Engineer",
             "Frontend Engineer",
             "DevOps Engineer",
             "Full Stack Engineer",
            "AI Engineer"
            ],
            label="Select Role",
            value="Software Engineer"
        )
        scrape_btn = gr.Button("Scrape Jobs")

    summary = gr.Markdown()

    with gr.Row():
        skills_chart = gr.Plot()
        tech_chart = gr.Plot()

    seniority_chart = gr.Plot()

    #Load insights on initial page load
    demo.load(
        load_insights,
        inputs=[role],
        outputs=[summary, skills_chart, tech_chart, seniority_chart]
    )

    #Auto-load insights on role change
    role.change(
        load_insights,
        inputs=[role],
        outputs=[summary, skills_chart, tech_chart, seniority_chart]
    )

    scrape_btn.click(
        scrape_and_refresh,
        inputs=[role],
        outputs=[summary, skills_chart, tech_chart, seniority_chart]
    )

demo.launch()