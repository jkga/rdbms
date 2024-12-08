import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

class SQLQueryPlanSelector :
  def __init__ (self, plans):
    self.plans        = plans
    self.selectedPlan = None

    self.__select (self.plans)

  def __select (self, plans):

    for plan in plans:
      if 'costs' in plan:
        if self.selectedPlan == None:
          self.selectedPlan = plan
        else:
          if ('costs' in self.selectedPlan):
            # save if the cost is lesser than the previous one
            if self.selectedPlan['costs'] > plan['cost']:
              self.selectedPlan = plan
    
    return self
  
  def getResults (self):
    return self.selectedPlan
 