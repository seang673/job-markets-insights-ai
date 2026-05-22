import gradio as gr
import requests
import plotly.express as px

API = "http://localhost:8000"

#Loading and displaying insights for job
def load_insights(role):
    res = requests.get(f"{API}/api/insights/overview?role={role}").json()
    if (
        "top_skills" not in res
        or not res["top_skills"]
        or res.get("total_jobs", 0) == 0
    ):
        msg = f"**No job data found for '{role}'.**\nTry scraping first."
        empty_fig = px.scatter()  # blank placeholder chart
        return msg, empty_fig, empty_fig, empty_fig

    # Build charts
    skills_fig = px.bar(
        res["top_skills"],
        x="count",
        y="name",
        orientation="h",
        title="Top Skills",
        color_discrete_sequence=["#636EFA"]
    )

    tech_fig = px.bar(
        res["top_tech_stack"],
        x="count",
        y="name",
        orientation="h",
        title="Top Tech Stack",
        color_discrete_sequence=["#EF553B"]
    )

    seniority_fig = px.pie(
        res["seniority_distribution"],
        names="level",
        values="count",
        title="Seniority Distribution"
    )

    summary = f"**Total Number of {res['role']} Jobs:** {res['total_jobs']}  \n**Role:** {res['role']}"

    return summary, skills_fig, tech_fig, seniority_fig

#Scraping jobs and refreshing insights
def scrape_and_refresh(role):
    yield (
          # button
        None, None, None, None,  # placeholders for charts/summary
        gr.update(value="Scraping...", interactive=False),
        gr.update(value="Delete All Scraped Jobs for This Role", variant="stop", interactive=False)
    )
    gr.Info(f"Scraping more jobs for {role}, this usually takes around 1 minute...")

    # Trigger scraping
    requests.post(f"{API}/api/scrape?role={role}")

    gr.Info("Scraping complete!")

    # After scraping, fetch updated insights
    summary, skills_fig, tech_fig, seniority_fig = load_insights(role)

    yield(
        summary,
        skills_fig,
        tech_fig,
        seniority_fig,
        gr.update(value="Scrape More Jobs", interactive=True),
        gr.update(value="Delete All Scraped Jobs for This Role", variant="stop", interactive=True)
    )

    return (summary, skills_fig, tech_fig, seniority_fig, gr.update(value="Scrape More Jobs", interactive=True))

#Delete jobs for role
def delete_jobs(role):
    try:
        resp = requests.delete(f"{API}/api/jobs", params={"role": role}).json()
        deleted = resp.get("deleted", 0)

        gr.Info(f"Deleted {deleted} jobs for role: {role}")

        # After deletion, refresh insights (will show empty charts)
        return load_insights(role)

    except Exception as e:
        gr.Error(f"Failed to delete jobs: {e}")
        return None, None, None, None


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
        scrape_btn = gr.Button(f"Scrape More Jobs")
        delete_btn = gr.Button("Delete All Scraped Jobs for This Role", variant="stop")

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
        outputs=[summary, skills_chart, tech_chart, seniority_chart, scrape_btn, delete_btn]
    )

    delete_btn.click(
        delete_jobs,
        inputs=[role],
        outputs=[summary, skills_chart, tech_chart, seniority_chart]
    )

demo.launch()