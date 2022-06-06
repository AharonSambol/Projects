using System;
using System.Collections.Generic;
using System.Linq;
using System.Diagnostics;
using System.Threading.Tasks;

/*
Trying to improve the built in sorting algorithm
My method works better when the same numbers repete multiple times
Basically just groups all the same numbers together, sorts, and expands the groups
The more complex one also groups numbers that are one away from each-other (cuz an int can't be 1.5)
*/

class Sort{
    static Random randNum = new Random();
    static void Main(string[] args){
        var watchNormal = new Stopwatch();
        var watchParallel = new Stopwatch();
        var watchSimple = new Stopwatch();
        var watchComplex = new Stopwatch();
        for (int i=0; i < 5; i++) {
            var arr = MakeRandArr();
            var arr2 = (int[]) arr.Clone();
            var arr3 = (int[]) arr.Clone();
            var arr4 = (int[]) arr.Clone();

            watchNormal.Start();
            BuiltInAlgo(arr);
            watchNormal.Stop();
            
            watchParallel.Start();
            ParallelSimple(arr2);
            watchParallel.Stop();
            
            watchSimple.Start();
            Simple(arr3);
            watchSimple.Stop();
            
            watchComplex.Start();
            ParallelSimple(arr4);
            watchComplex.Stop();            
        }

        var normal = watchNormal.ElapsedMilliseconds;
        var simple = watchSimple.ElapsedMilliseconds;
        var complex = watchComplex.ElapsedMilliseconds;
        var parallel = watchParallel.ElapsedMilliseconds;
        Console.WriteLine($"normal:  { normal }ms");
        Console.WriteLine($"simple:  { simple }ms");
        Console.WriteLine($"is { normal - simple }ms faster");
        Console.WriteLine($"cmplx:   { complex }ms");
        Console.WriteLine($"is { normal - complex }ms faster");
        Console.WriteLine($"parellel:{ parallel }ms");
        Console.WriteLine($"is { normal - parallel }ms faster");
    }
    static int[] MakeRandArr(){ // my algorithm would be a lot better if it's not completely random
        int[] arr = new int[10_000_000];
        for (int i = 0; i < arr.Length; i++){
            arr[i] = randNum.Next(-10_000, 10_000); // the smaller the range the better
        }
        return arr;
    }

    static int[] BuiltInAlgo(int[] arr){  
        Array.Sort(arr);
        return arr;
    }
    static int[] Simple(int[] arr){
        var dict = new Dictionary<int, int>();
        foreach(var item in arr) {
            if(!dict.TryGetValue(item, out int val)){
                if(dict.Keys.Count > 100_000){  // give up
                    Array.Sort(arr);
                    return arr;
                }
            }
            dict[item] = val + 1;
        }
        var sorted = dict.Keys.OrderBy(x => x);
        var res = new int[arr.Length];
        int i = 0;
        foreach(var item in sorted) {
            for (int k=0; k < dict[item]; k++) {
                res[i++] = item;
            }
        }
        return res;
    }
    static int[] Complex(int[] arr){
        var dict = new Dictionary<int, Nums>();
        var vals = new LinkedList<Nums>();
        for (int i=0; i < arr.Length; i++) {
            var item = arr[i];
            int cnt = 1;            
            while(i+1 < arr.Length && arr[i+1] == item){
                cnt++;
                i++;
            }
            if(dict.TryGetValue(item, out Nums nums)){
                nums.list[item - nums.startNum] += cnt;
            } else if(dict.TryGetValue(item + 1, out Nums nums1)){
                dict[item] = nums1;
                nums1.list.Insert(0, cnt);
                nums1.startNum -= 1;
            } else if(dict.TryGetValue(item - 1, out Nums nums2)){
                dict[item] = nums2;
                nums2.list.Add(cnt);
            } else {
                if(vals.Count > 100_000){   // give up
                    Array.Sort(arr);
                    return arr;
                }
                var nums3 = new Nums(item, cnt);
                dict[item] = nums3;
                vals.AddLast(nums3);
            }
        }
        int j = 0;
        foreach(var item in vals.OrderBy(x => x.startNum)) {
            var num = item.startNum;
            foreach(var amount in item.list) {
                for (int k=0; k < amount; k++) {
                    arr[j++] = num;
                }
                num++;
            }
        }
        return arr;
    }   
    static int[] ParallelSimple(int[] arr){
        int s = -9, e = 10;
        var tasks = new Dictionary<int, int>[e-s];
        Parallel.For(s, e, i => {
            tasks[i+9] = CalcCertain(arr, i);
        });
        IEnumerable<KeyValuePair<int, int>> vals = tasks[0];
        for (int q=1; q < tasks.Length; q++) {
            vals = vals.Concat(tasks[q]);
        }
        var sorted = vals.OrderBy(x => x.Key);
        int i = 0;
        foreach(var item in sorted) {
            for (int k=0; k < item.Value; k++) {
                arr[i++] = item.Key;
            }
        }
        return arr;
    }
    static Dictionary<int, int> CalcCertain(int[] arr, int task){
        var dict = new Dictionary<int, int>();
        foreach(var item in arr) {
            if(item % 10 != task){   continue; }
            dict.TryGetValue(item, out int val);
            dict[item] = val + 1;
        }
        return dict;
    }

}

class Nums {
    public Nums(int num, int count){
        startNum = num;
        list = new(){ count };
    }
    public int startNum;
    public List<int> list;
}