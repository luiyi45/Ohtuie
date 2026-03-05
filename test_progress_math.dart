
void main() {
  int avgCycle = 28;
  
  void testDay(int day) {
    int currentCycleDay = day;
    if (currentCycleDay > avgCycle) currentCycleDay = (currentCycleDay % avgCycle);
    if (currentCycleDay <= 0) currentCycleDay = 1;
    
    double progress = currentCycleDay / avgCycle;
    print("Day $day: currentCycleDay=$currentCycleDay, progress=${(progress * 100).toStringAsFixed(1)}%");
  }

  print("Testing cycle progress logic:");
  testDay(1);   // Start
  testDay(14);  // Mid
  testDay(28);  // End
  testDay(29);  // Overflow
  testDay(-1);  // Edge case
}
