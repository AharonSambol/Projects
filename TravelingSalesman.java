import java.util.ArrayList;
import java.util.LinkedList;

class Point{
    private int num;
    private int[][] map;
    public Point(int num, int[][] map){
        this.num = num;
        this.map = map;
    }

    public int distanceTo(Point other){
        return map[this.getNum()][other.getNum()];
    }

    public int getNum() {
        return num;
    }

    @Override
    public String toString() {
        return "Point{" + num + '}';
    }
}

public class TravelingSalesman {

    public static void main(String[] args) {
        int[][] matrix = new int[][]{
            {0,343,482,294,452,406,118,68},
            {343,0,3,129,115,165,45,15},
            {482,3,0,397,148,488,335,79},
            {294,129,397,0,32,135,318,310},
            {452,115,148,32,0,467,70,303},
            {406,165,488,135,467,0,83,63},
            {118,45,335,318,70,83,0,421},
            {68,15,79,310,303,63,421,0},
        };
        var a  = approximate(matrix);

        int len = 0;
        int last = a.get(0);
        for (int i = 1; i < a.size(); i++) {
            len += matrix[last][a.get(i)];
            last = a.get(i);
        }
        System.out.println(len); //602
    }


    public static ArrayList<Integer> approximate(int[][] matrix) {
        Point[] points = new Point[matrix.length - 1];
        Point start = new Point(0, matrix);
        for (int i = 1; i < matrix.length; i++) {
            points[i-1] = new Point(i, matrix);
        }
        ArrayList<Point[]> result = tsp(points, start, start);
        ArrayList<Integer> ans = new ArrayList<>();
        int lookingFor = 0;
        while (result.size() > 0) {
            for (int j = 0; j < result.size(); j++) {
                int first = result.get(j)[0].getNum();
                int second = result.get(j)[1].getNum();
                if(first == lookingFor || second == lookingFor){
                    ans.add(lookingFor);
                    result.remove(j);
                    lookingFor = first==lookingFor ? second : first;
                    break;
                }
            }
        }
        ans.add(lookingFor);
        for(int i:ans){
            System.out.println(i);
        }
        return ans;
    }

    public static ArrayList<Point[]> tsp(Point[] allPoints, Point start, Point end){
        ArrayList<Point[]> allPaths = new ArrayList<>();
        allPaths.add(new Point[]{start, end});

        for (Point point : allPoints) {
            int shortestDistance = Integer.MAX_VALUE;
            Point[] shortestPath = null;
            for(Point[] path : allPaths){
                int stretch = calcNewDistance(path, point);
                if(stretch < shortestDistance){
                    shortestDistance = stretch;
                    shortestPath = path;
                }
            }
            allPaths.remove(shortestPath);
            allPaths.add(0, new Point[]{shortestPath[0], point});
            allPaths.add(0, new Point[]{shortestPath[1], point});
        }
        RecheckLines(allPaths, allPoints);
        return allPaths;
    }
    static int calcNewDistance(Point[] path, Point newPoint){
        int newDis = path[0].distanceTo(newPoint) + path[1].distanceTo(newPoint);
        int oldDis = path[0].distanceTo(path[1]);
        return newDis - oldDis;
    }

    static void RecheckLines(ArrayList<Point[]> allPaths, Point[] allPoints){
        boolean changed = true;
        while(changed) {
            changed = false;
            for (Point point : allPoints) {
                int[] paths = findPathPointIn(allPaths,point);
                Point[] path1 = allPaths.get(paths[0]);
                Point[] path2 = allPaths.get(paths[1]);
                float minDistance = costDistance(point, allPaths.get(paths[0]), allPaths.get(paths[1]));
                Point[] newPath = null;
                for (int i = 0; i < allPaths.size(); i++) {
                    if(i == paths[0] || i == paths[1]){continue;}
                    Point[] path = allPaths.get(i);
                    float thisDistance = calcNewDistance(path, point);
                    if(thisDistance < minDistance){
                        minDistance = thisDistance;
                        newPath = path;
                    }
                }
                if(newPath != null) {
                    allPaths.remove(path1);
                    allPaths.remove(path2);
                    allPaths.add(0, new Point[]{path1[0].equals(point)? path1[1]: path1[0],path2[0].equals(point)? path2[1]: path2[0]});
                    allPaths.remove(newPath);
                    allPaths.add(0, new Point[]{newPath[0], point});
                    allPaths.add(0, new Point[]{newPath[1], point});
                    changed = true;
                }
            }
        }
    }
    public static int[] findPathPointIn(ArrayList<Point[]> allPaths, Point point){
        int[] paths = new int[2];
        int pos = 0;
        for (int i = 0; i < allPaths.size(); i++) {
            Point[] path = allPaths.get(i);
            if(path[0].equals(point) || path[1].equals(point)) {
                paths[pos] = i;
                pos++;
            }
        }
        return paths;
    }

    public static float costDistance(Point point, Point[] path1, Point[] path2){
        Point otherPoint1 = path1[0].equals(point)? path1[1]: path1[0];
        Point otherPoint2 = path2[0].equals(point)? path2[1]: path2[0];
        float currentLen = point.distanceTo(otherPoint1) + point.distanceTo(otherPoint2);
        float lenWithout = otherPoint1.distanceTo(otherPoint2);
        return currentLen - lenWithout;
    }
}
