from base64 import b64decode
import io
import json
from math import sqrt
import random
import time

from PIL import Image


class Point:

    def __init__(self, coordinates):
        self.coordinates = coordinates


class Cluster:

    def __init__(self, center, points):
        self.center = center
        self.points = points


class KMeans:

    def __init__(self, n_clusters, min_diff=1):
        self.n_clusters = n_clusters
        self.min_diff = min_diff

    def calculate_center(self, points):
        n_dim = len(points[0].coordinates)
        vals = [0.0 for i in range(n_dim)]
        for p in points:
            for i in range(n_dim):
                vals[i] += p.coordinates[i]
        coords = [(v / len(points)) for v in vals]
        return Point(coords)

    def assign_points(self, clusters, points):
        plists = [[] for i in range(self.n_clusters)]

        for p in points:
            smallest_distance = float('inf')

            for i in range(self.n_clusters):
                distance = euclidean(p, clusters[i].center)
                if distance < smallest_distance:
                    smallest_distance = distance
                    idx = i

            plists[idx].append(p)

        return plists

    def fit(self, points):
        clusters = [Cluster(center=p, points=[p])
                    for p in random.sample(points, self.n_clusters)]

        while True:

            plists = self.assign_points(clusters, points)

            diff = 0

            for i in range(self.n_clusters):
                if not plists[i]:
                    continue
                old = clusters[i]
                center = self.calculate_center(plists[i])
                new = Cluster(center, plists[i])
                clusters[i] = new
                diff = max(diff, euclidean(old.center, new.center))

            if diff < self.min_diff:
                break

        return clusters


def euclidean(p, q):
    n_dim = len(p.coordinates)
    return sqrt(sum(
        (p.coordinates[i] - q.coordinates[i]) ** 2 for i in range(n_dim)
    ))


def get_points(image):
    img = Image.open(io.BytesIO(image))
    img.thumbnail((128, 128))
    img = img.convert("RGB")
    w, h = img.size

    points = []
    for count, color in img.getcolors(w * h):
        for _ in range(count):
            points.append(Point(color))

        return points


def rgb_to_hex(rgb):
    return '#%s' % ''.join(('%02x' % p for p in rgb))


def detect_colors(frame, models):
    n_colors = 3
    imgdata = b64decode(frame)
    points = get_points(imgdata)
    if(len(points) < n_colors):
        n_colors = len(points)
    start = time.time()
    clusters = KMeans(n_clusters=n_colors).fit(points)
    clusters.sort(key=lambda c: len(c.points), reverse=True)
    rgbs = [map(int, c.center.coordinates) for c in clusters]
    colorsList = list(map(rgb_to_hex, rgbs))
    end = time.time()
    colors = []
    for c in colorsList:
        color = {"color": c}
        colors.append(json.dumps(color))

    elapsed_time = end - start
    output = {"inference_model": "Color Palette Detection", "inference_results": colors,
              "inference_start_time": round(start, 4), "inference_time": round(elapsed_time, 4)}
    return json.dumps(output)
