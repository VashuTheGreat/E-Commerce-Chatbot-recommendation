import pandas as pd
import logging
import ast
from src.utils.asyncHandler import asyncHandler
from src.entity.data_access import Connect_data
from src.constants import DATA_PATH
from langchain_core.tools import tool

@tool(description="Executes python code on the dataframe df to query and answer user questions.")
@asyncHandler
async def code_runner(code: str):
    logging.info("code_runner tool - entering tool execution")
    logging.info(f"code_runner tool - code payload:\n{code}")
    logging.info("code_runner tool - establishing data connection and loading dataframe")
    df = await Connect_data(DATA_PATH).load_data()
    local_vars = {"df": df, "pd": pd}
    logging.info(f"code_runner tool - loaded dataframe shape: {df.shape if hasattr(df, 'shape') else 'unknown'}")
    try:
        logging.info("code_runner tool - parsing python code into AST tree")
        tree = ast.parse(code)
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            logging.info("code_runner tool - last node is an expression. separating it for evaluation")
            last_expr = tree.body.pop()
            logging.info("code_runner tool - executing prefix code statements")
            exec(compile(tree, filename="<ast>", mode="exec"), {}, local_vars)
            logging.info("code_runner tool - evaluating last expression and assigning to result")
            eval_res = eval(compile(ast.Expression(last_expr.value), filename="<ast>", mode="eval"), {}, local_vars)
            if 'result' not in local_vars:
                local_vars['result'] = eval_res
        else:
            logging.info("code_runner tool - executing standard code block")
            exec(code, {}, local_vars)
        result = local_vars.get('result', "Code executed successfully")
        logging.info(f"code_runner tool - execution succeeded. result output: {result}")
        return str(result)
    except Exception as e:
        logging.error(f"code_runner tool - error raised during execution: {e}", exc_info=True)
        return f"Error: {str(e)}"