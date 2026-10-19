from pathlib import Path
import json
from threading import RLock
from flask import Flask, render_template, request, jsonify

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
AIRPORTS_FILE = DATA_DIR / "airports.json"
ROUTES_FILE = DATA_DIR / "routes.json"
_lock = RLock()

def read_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

def write_json(path, data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    temp.replace(path)

def airports_data(): return read_json(AIRPORTS_FILE)
def routes_data(): return read_json(ROUTES_FILE)
def save_airports(data): write_json(AIRPORTS_FILE, data)
def save_routes(data): write_json(ROUTES_FILE, data)
def airport_dict(a): return dict(a)
def route_dict(r, by_id):
    out = dict(r)
    out["source_code"] = by_id.get(r["source_id"], {}).get("code", "?")
    out["destination_code"] = by_id.get(r["destination_id"], {}).get("code", "?")
    return out

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "development-only-change-if-deploying"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for path in (AIRPORTS_FILE, ROUTES_FILE):
        if not path.exists(): write_json(path, [])

    @app.get("/")
    def index(): return render_template("index.html")

    @app.get("/api/health")
    def health():
        try:
            airports_data(); routes_data()
            return jsonify(status="ok", storage="JSON files", files=["data/airports.json", "data/routes.json"])
        except Exception as exc:
            return jsonify(status="error", message=str(exc)), 500

    @app.get("/api/airports")
    def get_airports(): return jsonify(sorted(airports_data(), key=lambda a: a["code"]))

    @app.post("/api/airports")
    def create_airport():
        data = request.get_json(silent=True) or {}
        try:
            code=str(data.get("code", "")).strip().upper(); name=str(data.get("name", "")).strip(); city=str(data.get("city", "")).strip()
            lat=float(data["lat"]); lon=float(data["lon"])
            if not code or not name or not city: return jsonify(error="Code, airport name and city are required."), 400
            if len(code)>5: return jsonify(error="Airport code must be 5 characters or fewer."), 400
            if not (-90<=lat<=90 and -180<=lon<=180): return jsonify(error="Latitude/longitude are outside valid ranges."), 400
            with _lock:
                airports=airports_data()
                if any(a["code"]==code for a in airports): return jsonify(error="That airport code already exists."), 409
                airport={"id":max((a["id"] for a in airports),default=0)+1,"code":code,"name":name,"city":city,"lat":lat,"lon":lon}
                airports.append(airport); save_airports(airports)
            return jsonify(airport), 201
        except (KeyError,TypeError,ValueError): return jsonify(error="Provide valid numeric latitude and longitude."), 400

    @app.put("/api/airports/<int:airport_id>")
    def update_airport(airport_id):
        data=request.get_json(silent=True) or {}
        try:
            with _lock:
                airports=airports_data(); airport=next((a for a in airports if a["id"]==airport_id),None)
                if not airport: return jsonify(error="Airport not found."),404
                updated={"id":airport_id,"code":str(data.get("code",airport["code"])).strip().upper(),"name":str(data.get("name",airport["name"])).strip(),"city":str(data.get("city",airport["city"])).strip(),"lat":float(data.get("lat",airport["lat"])),"lon":float(data.get("lon",airport["lon"]))}
                if not updated["code"] or not updated["name"] or not updated["city"]: return jsonify(error="Code, airport name and city are required."),400
                if not (-90<=updated["lat"]<=90 and -180<=updated["lon"]<=180): return jsonify(error="Latitude/longitude are outside valid ranges."),400
                if any(a["id"]!=airport_id and a["code"]==updated["code"] for a in airports): return jsonify(error="That airport code already exists."),409
                airports[airports.index(airport)]=updated; save_airports(airports)
            return jsonify(updated)
        except (TypeError,ValueError): return jsonify(error="Invalid airport values."),400

    @app.delete("/api/airports/<int:airport_id>")
    def delete_airport(airport_id):
        with _lock:
            airports=airports_data(); airport=next((a for a in airports if a["id"]==airport_id),None)
            if not airport: return jsonify(error="Airport not found."),404
            save_airports([a for a in airports if a["id"]!=airport_id])
            save_routes([r for r in routes_data() if r["source_id"]!=airport_id and r["destination_id"]!=airport_id])
        return jsonify(message="Airport and its connected routes deleted.")

    @app.get("/api/routes")
    def get_routes():
        by_id={a["id"]:a for a in airports_data()}
        return jsonify([route_dict(r,by_id) for r in sorted(routes_data(),key=lambda r:r["id"])])

    @app.post("/api/routes")
    def create_route():
        data=request.get_json(silent=True) or {}
        try:
            source_id=int(data["source_id"]); destination_id=int(data["destination_id"]); distance=float(data["distance"])
            if source_id==destination_id: return jsonify(error="Source and destination must be different."),400
            if distance<=0: return jsonify(error="Distance must be greater than zero."),400
            with _lock:
                airports=airports_data(); ids={a["id"] for a in airports}
                if source_id not in ids or destination_id not in ids: return jsonify(error="Choose two existing airports."),400
                routes=routes_data()
                if any({r["source_id"],r["destination_id"]}=={source_id,destination_id} for r in routes): return jsonify(error="That route already exists. Edit or restore it instead."),409
                route={"id":max((r["id"] for r in routes),default=0)+1,"source_id":source_id,"destination_id":destination_id,"distance":distance,"active":bool(data.get("active",True))}
                routes.append(route); save_routes(routes); by_id={a["id"]:a for a in airports}
            return jsonify(route_dict(route,by_id)),201
        except (KeyError,TypeError,ValueError): return jsonify(error="Provide valid source, destination and distance."),400

    @app.put("/api/routes/<int:route_id>")
    def update_route(route_id):
        data=request.get_json(silent=True) or {}
        try:
            with _lock:
                routes=routes_data(); route=next((r for r in routes if r["id"]==route_id),None)
                if not route: return jsonify(error="Route not found."),404
                if "distance" in data:
                    distance=float(data["distance"])
                    if distance<=0: return jsonify(error="Distance must be greater than zero."),400
                    route["distance"]=distance
                if "active" in data: route["active"]=bool(data["active"])
                save_routes(routes); by_id={a["id"]:a for a in airports_data()}; result=route_dict(route,by_id)
            return jsonify(result)
        except (TypeError,ValueError): return jsonify(error="Invalid route values."),400

    @app.delete("/api/routes/<int:route_id>")
    def delete_route(route_id):
        with _lock:
            routes=routes_data(); route=next((r for r in routes if r["id"]==route_id),None)
            if not route: return jsonify(error="Route not found."),404
            save_routes([r for r in routes if r["id"]!=route_id])
        return jsonify(message="Route deleted.")

    @app.post("/api/route")
    def find_route():
        data=request.get_json(silent=True) or {}
        try: start_id=int(data["start_id"]); end_id=int(data["end_id"]); mode=data.get("mode","dijkstra"); blocked_id=int(data["blocked_route_id"]) if data.get("blocked_route_id") else None
        except (KeyError,TypeError,ValueError): return jsonify(error="Choose a starting and destination airport."),400
        airport_list=airports_data(); airports={a["id"]:a for a in airport_list}
        if start_id not in airports or end_id not in airports: return jsonify(error="Selected airport no longer exists."),404
        if start_id==end_id: return jsonify(error="Choose two different airports."),400
        routes=[r for r in routes_data() if r["active"] and r["id"]!=blocked_id]
        adjacency={aid:[] for aid in airports}
        for r in routes:
            adjacency[r["source_id"]].append((r["destination_id"],r["distance"],r["id"]))
            adjacency[r["destination_id"]].append((r["source_id"],r["distance"],r["id"]))
        path,total=bfs_path(adjacency,start_id,end_id) if mode=="bfs" else dijkstra_path(adjacency,start_id,end_id)
        if not path: return jsonify(error="No available route connects these airports."),404
        used=[]
        for i in range(len(path)-1):
            matches=[(dist,rid) for neighbor,dist,rid in adjacency[path[i]] if neighbor==path[i+1]]
            if matches:
                dist,rid=min(matches); used.append({"id":rid,"distance":dist})
        return jsonify(mode=mode,airports=[airports[aid] for aid in path],airport_ids=path,route_ids=[x["id"] for x in used],legs=used,total_distance=round(total,2),stops=max(0,len(path)-2),note=("BFS finds the fewest flight legs; distance is not necessarily minimum." if mode=="bfs" else "Dijkstra finds the minimum total distance."))

    @app.post("/api/diversion")
    def find_diversion():
        data=request.get_json(silent=True) or {}
        if not data.get("start_id") or not data.get("end_id") or not data.get("blocked_route_id"): return jsonify(error="Choose start, destination, and a route to close."),400
        data["mode"]="dijkstra"
        with app.test_request_context(json=data): return find_route()
    return app

def dijkstra_path(adjacency,start,end):
    import heapq
    distances={node:float("inf") for node in adjacency}; previous={}; distances[start]=0; queue=[(0,start)]
    while queue:
        cost,node=heapq.heappop(queue)
        if cost!=distances[node]: continue
        if node==end: break
        for neighbor,weight,_ in adjacency[node]:
            candidate=cost+weight
            if candidate<distances[neighbor]: distances[neighbor]=candidate; previous[neighbor]=node; heapq.heappush(queue,(candidate,neighbor))
    if distances[end]==float("inf"): return [],0
    path=[]; current=end
    while current!=start: path.append(current); current=previous[current]
    path.append(start); path.reverse(); return path,distances[end]

def bfs_path(adjacency,start,end):
    from collections import deque
    queue=deque([start]); previous={start:None}
    while queue:
        node=queue.popleft()
        if node==end: break
        for neighbor,_,_ in adjacency[node]:
            if neighbor not in previous: previous[neighbor]=node; queue.append(neighbor)
    if end not in previous: return [],0
    path=[]; node=end
    while node is not None: path.append(node); node=previous[node]
    path.reverse(); total=0
    for a,b in zip(path,path[1:]): total+=min(d for n,d,_ in adjacency[a] if n==b)
    return path,total

app=create_app()
if __name__ == "__main__": app.run(debug=True)
