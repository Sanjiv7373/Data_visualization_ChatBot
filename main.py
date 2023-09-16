from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import pandas as pd
from pydantic import BaseModel
import openai
import mysql.connector
import plotly.express as px

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# OpenAI API key
openai.api_key = "YOUR_API_KEY"

# MySQL connection setup
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="company",
    auth_plugin='mysql_native_password'
)
db_cursor = db_connection.cursor()

class UserInput(BaseModel):
    user_input: str
def generate_sql_query_with_openai(query, table_descriptions):
    system_prompt = "you are a text-to-SQL translator. You write MySQL code based on plain-language prompts."
    user_prompt = f"""
    - Language: MySQL
    - Table and column: {table_descriptions}
    You are a SQL code translator. Your role is to translate natural language to MySQL. Your only output should be SQL code. Do not include any other text. Only SQL code.
    Translate the following prompt to a syntactically-correct MySQL query:
    {query}
    """
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=user_prompt,
        max_tokens=100,
    )
    
    return response.choices[0].text.strip()


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index1.html", {"request": request})
global df
@app.post("/chartbot")
async def chatbot_interaction(data: UserInput):
    user_input = data.user_input
    words = user_input.split()
    chart_type = None


    chart_keywords = {
    "bar": ["bar", "bar chart"],
    "scatter": ["scatter", "scatter plot"],
    "line": ["line", "line chart"],
    "box": ["box", "box plot"],
    "pie": ["pie", "pie chart"],
    "histogram": ["histogram"],
    "area": ["area", "area chart"],
    "heatmap": ["heatmap"],
    "bar_polar": ["bar polar", "polar bar"],
    "line3d": ["line 3d", "line3d", "3d line"],
    "violin": ["violin", "violin plot"],
    "pairplot": ["pairplot", "pair plot"],
    "box_violin": ["box violin", "box violin plot"],
    "funnel": ["funnel", "funnel plot"],
    "density_heatmap": ["density heatmap", "density heatmap plot"],
    "waterfall": ["waterfall", "waterfall chart"],
    "scatter_matrix": ["scatter matrix", "scatter matrix plot"],

    }

    for word in words:
        if word.lower() in chart_keywords:
            chart_type = word.lower()
            break
    try:
        # Fetch table descriptions
        db_cursor.execute("SHOW TABLES")
        tables = [table[0] for table in db_cursor.fetchall()]

        table_descriptions = {}
        for table in tables:
            db_cursor.execute(f"DESCRIBE {table}")
            columns = [column[0] for column in db_cursor.fetchall()]
            table_descriptions[table] = columns
        print(table_descriptions)

        #openai_prompt = f"Generate an SQL query for creating a Plotly chart.User Request: {user_input} Table Descriptions: {table_descriptions}and make use of the table descriptions to construct a complete only MySQL query with meaningful aliases for each column."
        openai_prompt=user_input
        sql_query = generate_sql_query_with_openai(user_input, table_descriptions)
        print(sql_query)

        # Execute the SQL query and fetch the results using Pandas
        df = pd.read_sql(sql_query, db_connection)
        print(df)

        #  dynamically
        x_column_name = df.columns[0]
        y_column_name = df.columns[1]

        # selected chart type
        if chart_type == "bar":
            chart = px.bar(df, x=x_column_name, y=y_column_name, title='Bar Chart')
        elif chart_type == "scatter":
            chart = px.scatter(df, x=x_column_name, y=y_column_name, title='Scatter Plot')
        elif chart_type == "line":
            chart = px.line(df, x=x_column_name, y=y_column_name, title='Line Chart')
        elif chart_type == "box":
            chart = px.box(df, x=x_column_name, y=y_column_name, title='Box Plot')
        elif chart_type == "pie":
            chart = px.pie(df, values=y_column_name, names=x_column_name, title='Pie Chart')
        elif chart_type == "histogram":
            chart = px.histogram(df, x=x_column_name, y=y_column_name, title='Histogram')
        elif chart_type == "area":
            chart = px.area(df, x=x_column_name, y=y_column_name, title='Area Chart')
        elif chart_type == "heatmap":
            chart = px.imshow(df.corr(), title='Heatmap')
        elif chart_type == "bar_polar" or chart_type == "bar polar" or chart_type == "polar bar":
            chart = px.bar_polar(df, r=y_column_name, theta=x_column_name, title='Polar Bar Chart')
        elif chart_type == "line3d" or chart_type == "line 3d" or chart_type == "3D line":
            chart = px.line_3d(df, x=x_column_name, y=y_column_name, z=y_column_name, title='3D Line Chart')
        elif chart_type == "violin":
            chart = px.violin(df, x=x_column_name, y=y_column_name, title='Violin Plot')
        elif chart_type == "pairplot":
            chart = px.scatter_matrix(df, dimensions=[x_column_name, y_column_name], title='Pair Plot')
        elif chart_type == "box_violin":
            chart = px.box_violin(df, x=x_column_name, y=y_column_name, title='Box Violin Plot')
        elif chart_type == "funnel":
            chart = px.funnel(df, x=x_column_name, y=y_column_name, title='Funnel Plot')
        elif chart_type == "density_heatmap":
            chart = px.density_heatmap(df, x=x_column_name, y=y_column_name, title='Density Heatmap')
        elif chart_type == "waterfall":
            chart = px.waterfall(df, x=x_column_name, y=y_column_name, title='Waterfall Chart')
        elif chart_type == "scatter_matrix":
            chart = px.scatter_matrix(df, title='Scatter Matrix')


        # Convert the Plotly chart to JSON format
        chart_json = chart.to_json()#22/08/2023
        print(sql_query)

        return {"chart": chart_json}

    except Exception as e:
        print("Error:", e)
        return {"response": "An error occurred while processing the request."}
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
