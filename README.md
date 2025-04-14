# Genetic Algorithm for Automated Test Case Generation

This project implements a genetic algorithm (GA) to automatically generate test cases for a date validation function. The aim is to maximize coverage of all date categories—including valid dates, invalid dates, and boundary cases—by evolving diverse date strings in the format **DD/MM/YYYY**.

---

## Project Overview

**Objective:**  
Design and implement a GA that generates input test cases for a date validation function. The function checks if a date string represents a real calendar date (e.g., "15/05/2023") and distinguishes between valid and invalid dates (e.g., "31/04/2023" or "29/02/2021").

**Key Features:**
- **Chromosome Representation:** Each test case is modeled as a tuple `(day, month, year)`. The system allows initial random generation, including potentially invalid dates to encourage diversity.
- **Fitness Function:** Test cases are rewarded based on their novelty. The fitness function rewards newly covered date categories (e.g., leap years, 30-day months) and penalizes redundant cases.
- **Genetic Operators:**  
  - **Selection:** Rank-based selection picks top-performing test cases.
  - **Crossover:** Children are produced by swapping parts of parent date values.
  - **Mutation:** With a fixed mutation rate, date values are perturbed (day ±3, month ±1, year ± range modifications) to maintain diversity.
- **Local Search Refinement (Bonus):** An additional local search strategy refines test cases after the GA run, improving category coverage further.
- **Output:** The program prints the best-evolved test cases along with their categories and overall coverage percentage. It also saves the test cases to CSV files and produces a line graph (`coverage_history.png`) showing how coverage improves over generations.

---

## Implementation Details

### Main Components:
- **Date Validation and Categorization Functions:**  
  - `valid8Date(date_str)` checks if a date string is valid.
  - `categore_date(d, m, y)` categorizes the date (e.g., valid, invalid, boundary) based on its properties.
  
- **Chromosome Representation (`DateChromo`):**  
  Represents an individual test case with random initialization and methods for mutation, date string conversion, and category evaluation.

- **Genetic Algorithm Core (`GenAlg`):**  
  Manages population initialization, fitness evaluation, parent selection, crossover, elitism, and generation updates.  
  - **Elitism:** Retains the top 10% of the population unchanged.
  - **Coverage Tracking:** Monitors the percentage of target test categories achieved.
  
- **Local Search Refinement:**  
  A method (`localSearchRefine`) that further refines the GA results to boost test coverage by exploring new date combinations.

- **Output Functions:**  
  Functions to save the generated test cases to CSV files and to plot the coverage history over generations.

---

## Requirements

### Software:
- **Python 3.x**

### Libraries:
- **Built-in:** `random`, `re`, `collections`
- **Third-party:** `matplotlib` (install via `pip install matplotlib` if not already available)

---

## Installation & Execution

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

 2. **Install Dependencies**:
    Ensure that Python 3 is installed and that matplotlib is available:
```bash
pip install matplotlib
```

3. **Run the Application:**
   ```bash
   python main.py
   ```

- This will start the genetic algorithm, display generation progress in the terminal, and generate:
- CSV files with the best-evolved test cases (ga_test_cases.csv and refined_test_cases.csv).
- A coverage history graph saved as coverage_history.png.



