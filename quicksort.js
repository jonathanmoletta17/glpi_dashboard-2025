/**
 * Quicksort Algorithm Implementation in JavaScript
 * 
 * Quicksort is a highly efficient sorting algorithm that uses a divide-and-conquer approach.
 * It works by selecting a 'pivot' element from the array and partitioning the other elements
 * into two sub-arrays according to whether they are less than or greater than the pivot.
 * 
 * Time Complexity:
 * - Best Case: O(n log n)
 * - Average Case: O(n log n)
 * - Worst Case: O(n²) - when the pivot is always the smallest or largest element
 * 
 * Space Complexity: O(log n) - due to the recursive call stack
 * 
 * @param {number[]} arr - Array of numbers to be sorted
 * @param {number} low - Starting index (default: 0)
 * @param {number} high - Ending index (default: arr.length - 1)
 * @returns {number[]} - Sorted array
 */
function quicksort(arr, low = 0, high = arr.length - 1) {
    if (low < high) {
        // Partition the array and get the pivot index
        const pivotIndex = partition(arr, low, high);
        
        // Recursively sort elements before and after partition
        quicksort(arr, low, pivotIndex - 1);
        quicksort(arr, pivotIndex + 1, high);
    }
    
    return arr;
}

/**
 * Partition function for quicksort
 * Places the pivot element at its correct position in sorted array
 * and places all smaller elements to left of pivot and all greater elements to right
 * 
 * @param {number[]} arr - Array to partition
 * @param {number} low - Starting index
 * @param {number} high - Ending index
 * @returns {number} - Index of the pivot element after partitioning
 */
function partition(arr, low, high) {
    // Choose the rightmost element as pivot
    const pivot = arr[high];
    
    // Index of smaller element (indicates the right position of pivot found so far)
    let i = low - 1;
    
    for (let j = low; j < high; j++) {
        // If current element is smaller than or equal to pivot
        if (arr[j] <= pivot) {
            i++; // Increment index of smaller element
            swap(arr, i, j);
        }
    }
    
    // Place pivot at correct position
    swap(arr, i + 1, high);
    return i + 1;
}

/**
 * Utility function to swap two elements in an array
 * 
 * @param {number[]} arr - Array containing elements to swap
 * @param {number} i - Index of first element
 * @param {number} j - Index of second element
 */
function swap(arr, i, j) {
    const temp = arr[i];
    arr[i] = arr[j];
    arr[j] = temp;
    [arr[i], arr[j]] = [arr[j], arr[i]];
}

/**
 * Alternative implementation using random pivot for better average performance
 * 
 * @param {number[]} arr - Array of numbers to be sorted
 * @param {number} low - Starting index (default: 0)
 * @param {number} high - Ending index (default: arr.length - 1)
 * @returns {number[]} - Sorted array
 */
function quicksortRandomPivot(arr, low = 0, high = arr.length - 1) {
    if (low < high) {
        // Randomly select pivot and swap with last element
        const randomIndex = Math.floor(Math.random() * (high - low + 1)) + low;
        swap(arr, randomIndex, high);
        
        const pivotIndex = partition(arr, low, high);
        
        quicksortRandomPivot(arr, low, pivotIndex - 1);
        quicksortRandomPivot(arr, pivotIndex + 1, high);
    }
    
    return arr;
}

/**
 * Non-recursive (iterative) implementation of quicksort
 * Uses an explicit stack to avoid recursion overhead
 * 
 * @param {number[]} arr - Array of numbers to be sorted
 * @returns {number[]} - Sorted array
 */
function quicksortIterative(arr) {
    const stack = [];
    stack.push(0);
    stack.push(arr.length - 1);
    
    while (stack.length > 0) {
        const high = stack.pop();
        const low = stack.pop();
        
        if (low < high) {
            const pivotIndex = partition(arr, low, high);
            
            // Push left subarray bounds
            stack.push(low);
            stack.push(pivotIndex - 1);
            
            // Push right subarray bounds
            stack.push(pivotIndex + 1);
            stack.push(high);
            // To optimize stack depth, we process the smaller partition first.
            // This is done by pushing the larger partition's bounds onto the stack, then the smaller one.
            // This ensures the stack depth is at most O(log n).
            if ((pivotIndex - low) > (high - pivotIndex)) {
                // Left partition is larger, so push it first.
                if (low < pivotIndex - 1) {
                    stack.push(low);
                    stack.push(pivotIndex - 1);
                }
                // Then push the smaller right partition to be processed next.
                if (pivotIndex + 1 < high) {
                    stack.push(pivotIndex + 1);
                    stack.push(high);
                }
            } else {
                // Right partition is larger or equal, so push it first.
                if (pivotIndex + 1 < high) {
                    stack.push(pivotIndex + 1);
                    stack.push(high);
                }
                // Then push the smaller left partition to be processed next.
                if (low < pivotIndex - 1) {
                    stack.push(low);
                    stack.push(pivotIndex - 1);
                }
            }
        }
    }
    
    return arr;
}

// Example usage and testing
if (typeof module !== 'undefined' && module.exports) {
    // Node.js environment
    module.exports = {
        quicksort,
        quicksortRandomPivot,
        quicksortIterative,
        partition,
        swap
    };
} else {
    // Browser environment - add to global scope
    window.quicksort = quicksort;
    window.quicksortRandomPivot = quicksortRandomPivot;
    window.quicksortIterative = quicksortIterative;
}

// Demo function to test the implementations
function demonstrateQuicksort() {
    console.log('=== Quicksort Algorithm Demonstration ===\n');
    
    const testArrays = [
        [64, 34, 25, 12, 22, 11, 90],
        [5, 2, 8, 1, 9],
        [1],
        [],
        [3, 3, 3, 3],
        [9, 8, 7, 6, 5, 4, 3, 2, 1]
    ];
    
    testArrays.forEach((arr, index) => {
        console.log(`Test ${index + 1}:`);
        console.log('Original:', JSON.stringify(arr));
        
        // Test standard quicksort
        const arr1 = [...arr];
        quicksort(arr1);
        console.log('Quicksort:', JSON.stringify(arr1));
        
        // Test random pivot quicksort
        const arr2 = [...arr];
        quicksortRandomPivot(arr2);
        console.log('Random Pivot:', JSON.stringify(arr2));
        
        // Test iterative quicksort
        const arr3 = [...arr];
        quicksortIterative(arr3);
        console.log('Iterative:', JSON.stringify(arr3));
        
        console.log('---');
    });
}

// Uncomment the line below to run the demonstration
// demonstrateQuicksort();