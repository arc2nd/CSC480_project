import types
import datetime

USER_ATTRS = {'name': types.StringTypes, 
              'email': types.StringTypes, 
              'first': types.StringTypes, 
              'last': types.StringTypes, 
              'middle_name': types.StringTypes, 
              'full': types.StringTypes, 
              'dob': datetime.datetime, 
              'points': types.FloatType,  
              'style': types.StringType, 
              'timeout': types.IntType, 
              'pw_hash': types.StringType, 
              'id': types.IntType
             }

CHORE_ATTRS = {'name': types.StringTypes, 
               'desc': types.StringTypes, 
               'due': datetime.datetime, 
               'expired': types.BooleanType, 
               'points': types.FloatType, 
               'creator': types.StringTypes, 
               'assigned_to': types.StringTypes, 
               'done': datetime.datetime, 
               'id': types.IntType
               }

REWARD_ATTRS = {'name': types.StringTypes,
                'desc': types.StringTypes, 
                'due': datetime.datetime, 
                'expired': types.BooleanType, 
                'points': types.FloatType,  
                'creator': types.StringTypes, 
                'assigned_to': types.StringTypes, 
                'claimed': types.BooleanType, 
                'recurring': types.StringTypes, 
                'id': types.IntType
               }
