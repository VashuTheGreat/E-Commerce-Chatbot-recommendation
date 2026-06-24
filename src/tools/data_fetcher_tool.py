import pandas as pd
import logging
import ast
from src.utils.asyncHandler import asyncHandler
from src.entity.data_access import Connect_data

@asyncHandler
async def code_runner(code: str):
    """this is the tool to run and give output of the code entered.
    Args:
        code: python code to execute on the dataframe 'df'
        file_path: path to the csv file
    """
    logging.info(f"TOOL INPUT - Code to execute:\n{code}")
    
    df = Connect_data()
    local_vars = {"df": df, "pd": pd}
    
    try:
        # Parse the code into an AST
        tree = ast.parse(code)
        
        # If the last node is an expression, we handle it specially to capture its value
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last_expr = tree.body.pop()
            # Execute everything except the last expression
            exec(compile(tree, filename="<ast>", mode="exec"), {}, local_vars)
            # Evaluate the last expression and assign to result if not already set
            eval_res = eval(compile(ast.Expression(last_expr.value), filename="<ast>", mode="eval"), {}, local_vars)
            if 'result' not in local_vars:
                local_vars['result'] = eval_res
        else:
            exec(code, {}, local_vars)
            
        result = local_vars.get('result', "Code executed successfully")
        logging.info(f"TOOL OUTPUT: {result}")
        return str(result)
    except Exception as e:
        logging.error(f"TOOL ERROR: {e}")
        return f"Error: {str(e)}"