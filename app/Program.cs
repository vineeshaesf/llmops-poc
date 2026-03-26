// Console.WriteLine("Hello LLMOps");
using System;

class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("Hello LLMOps");

        int number = 10;
        string text = "20";


        int result = number + text;

        Console.WriteLine("Result is: " + result);

        // Another small logic mistake
        if (result = 30) // should be ==, but using assignment
        {
            Console.WriteLine("Result is 30");
        }
    }
}
