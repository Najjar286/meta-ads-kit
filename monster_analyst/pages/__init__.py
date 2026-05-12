"""Monster Analyst page modules — dynamically imported due to numeric prefixes."""
from importlib import import_module as _im

_1_Financial_Analysis = _im("monster_analyst.pages.1_Financial_Analysis")
_2_Funnel_Analysis = _im("monster_analyst.pages.2_Funnel_Analysis")
_3_Creative_Audit = _im("monster_analyst.pages.3_Creative_Audit")
_4_Algorithm_Health = _im("monster_analyst.pages.4_Algorithm_Health")
_5_Multi_Source_Report = _im("monster_analyst.pages.5_Multi_Source_Report")
_6_Messaging_Analysis = _im("monster_analyst.pages.6_Messaging_Analysis")
_7_Dashboard = _im("monster_analyst.pages.7_Dashboard")
_7_Settings = _im("monster_analyst.pages.7_Settings")
_8_Video_Analysis = _im("monster_analyst.pages.8_Video_Analysis")
_9_Deep_Analysis = _im("monster_analyst.pages.9_Deep_Analysis")
