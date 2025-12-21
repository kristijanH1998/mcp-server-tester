# How to Start the Project:
1.  Install Dependencies. Run:
- Install the latest version of Python and its associated pip package manager, using commands for your operating system.
- pip install fastapi uvicorn fastmcp mcp python-dotenv
2. Navigate to the project directory.
3. Run the server with: python mcp_server.py 
4. Run the backend client with: uvicorn backend:app --reload --port 8000
5. Run command to open the index.html frontend file in your browser: <browser_name> index.html
- You should now see an interface with options to register a server, select tools, and run experiments to test the MCP server.

# Design
- This is meant to be a simple full-stack MCP server inspector application which lets users choose a server to test, the tools that will be used, arguments that will be sent, and number of iterations to perform on those arguments.
- mcp_server is a basic FastMCP server with only an echo tool implemented, which returns textual input from requests.
- The backend comprises the imports and environment variables, CORS rules, data structures (for storing servers, clients, and experiment results), models for requests, helpers and tools, and code that processes experiment data upon request.
- The frontend is a basic HTML design whose primary purpose is to provide buttons, input fields, and fields for displaying results from servers. 
- The time it takes for each iteration to finish is recorded in the results that are returned and displayed. Mean time for all iterations is also computed. All potential errors in the process are spotted and reported back to the testing user.
- Language used to build this application was Python. The backend API is created with FastAPI framework.
- Integrity of data sent in requests and responses is preserved using Python's Pydantic library. Time recording and mean calculation are performed with tools from statistics and time libraries. To implement the Model Context Protocol, the FastMCP framework is used.

# AI Tools
- ChatGPT was utilized for generating certain sections of code, particularly the standard code structure for routes, middleware, and frontend HTML components. 
- Google Gemini was used for general information on various frameworks and libraries required to build the application, researching main concepts of MCP client-server interaction and how MCP servers are used by LLMs.