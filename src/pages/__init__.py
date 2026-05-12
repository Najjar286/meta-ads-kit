"""Ultimate Dashboard page modules — dynamically imported due to numeric prefixes."""
from importlib import import_module as _im

_01_Campaign_Manager = _im("src.pages.01_Campaign_Manager")
_02_Ad_Sets = _im("src.pages.02_Ad_Sets")
_03_Ads = _im("src.pages.03_Ads")
_04_Audiences = _im("src.pages.04_Audiences")
_05_Budget_Center = _im("src.pages.05_Budget_Center")
_06_Performance = _im("src.pages.06_Performance")
_07_Rules_Engine = _im("src.pages.07_Rules_Engine")
_08_AB_Testing = _im("src.pages.08_AB_Testing")
_09_Funnel_Attribution = _im("src.pages.09_Funnel_Attribution")
_10_Report_Builder = _im("src.pages.10_Report_Builder")
_11_Activity_Log = _im("src.pages.11_Activity_Log")
_12_Data_Studio = _im("src.pages.12_Data_Studio")
_13_Settings = _im("src.pages.13_Settings")
_14_Profile_Manager = _im("src.pages.14_Profile_Manager")
