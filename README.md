# Indian Flight Route Optimizer

A web-based flight route planning application built using Python, Flask, HTML, CSS, and JavaScript. The project uses graph algorithms to calculate shortest-distance routes, find minimum-stop paths, and simulate alternative routes when a connection becomes unavailable.

## Overview

Indian Flight Route Optimizer represents airports as vertices and routes as weighted edges in a graph. Users can select airports, calculate routes, visualize connections, and manage airport and route data through an interactive web interface.

The project demonstrates the practical application of graph algorithms in route optimization.

## Features

- **Shortest Route:** Uses Dijkstra’s algorithm to find the minimum-distance route between airports.
- **Minimum Stops:** Uses Breadth-First Search (BFS) to find a route with the minimum number of connections.
- **Route Diversion:** Simulates alternative routing when a connection is disabled.
- **Interactive Map:** Displays airports and their connections visually.
- **Airport Management:** Supports adding and deleting airports.
- **Route Management:** Supports connecting and disconnecting routes.
- **Route Visualization:** Highlights selected routes and displays route information.
- **JSON Storage:** Stores airport and route data in JSON files without requiring a separate database.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend logic and graph algorithms |
| Flask | Web application framework |
| HTML | Page structure |
| CSS | Interface styling |
| JavaScript | Frontend interactions and route visualization |
| JSON | Airport and route data storage |

## Algorithms Used

### 1. Dijkstra’s Algorithm

Dijkstra’s algorithm calculates the shortest path between a source airport and a destination airport using route distances as edge weights.

**Purpose:** Minimize the total distance travelled.

**Time Complexity:** Depends on the implementation. For a standard priority-queue implementation, it is typically \(O((V+E)\log V)\).

### 2. Breadth-First Search (BFS)

BFS explores the graph level by level to find a path with the minimum number of edges.

**Purpose:** Minimize the number of route connections, treating each connection equally.

**Time Complexity:** \(O(V+E)\), using an adjacency-list representation.

Here, \(V\) represents the number of airports and \(E\) represents the number of route connections.

## Project Structure

```text
Indian-Flight-Route-Optimizer/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── airports.json
│   └── routes.json
│
├── static/
│   ├── app.js
│   └── style.css
│
└── templates/
    └── index.html
```

## Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version
- pip
- Git (optional, for cloning the repository)

### Step 1: Clone the Repository

```bash
git clone https://github.com/harsh98720/Indian-Flight-Route-Optimizer.git
```

### Step 2: Open the Project Directory

```bash
cd Indian-Flight-Route-Optimizer
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment on Windows:

```bash
.venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
python app.py
```

Open the local URL displayed in the terminal. For a typical Flask development setup, this may be:

```text
http://127.0.0.1:5000
```

## Sample Test Results

The following results are from the project's illustrative dataset.

| Source | Destination | Algorithm / Scenario | Result |
|---|---|---|---|
| IXC | ATQ | Dijkstra | 205 km |
| IXC | DEL | Dijkstra | 240 km |
| IXC | DEL | BFS | 1 leg, 0 intermediate stops |
| IXC | DEL | Direct route disabled | IXC → ATQ → DEL, 635 km |

**Note:** These distances are illustrative values from the project dataset, not verified real-world flight distances or actual airline schedules.

## Data Storage

The application uses JSON files to store its data:

- `data/airports.json` — airport details, codes, and coordinates.
- `data/routes.json` — connections between airports and their distance values.

This file-based approach makes the project simple to run and maintain without a database server.

## Future Enhancements

- Integration with real-world airport and flight data.
- Live flight status and schedule integration.
- Weather-aware route recommendations.
- More advanced route optimization and operational constraints.
- Database integration for persistent and scalable data management.

## Learning Outcomes

This project demonstrates:

- Graph representation and traversal.
- Shortest-path algorithms.
- Breadth-First Search.
- Route optimization and alternative-path handling.
- Flask-based web application development.
- Frontend and backend integration.
- JSON-based data management.

## Author

**Harsh**  
Master of Computer Applications (MCA)  
Chandigarh University

## Repository

[Indian Flight Route Optimizer — GitHub](https://github.com/harsh98720/Indian-Flight-Route-Optimizer)

## License

This project was developed for academic and learning purposes.
