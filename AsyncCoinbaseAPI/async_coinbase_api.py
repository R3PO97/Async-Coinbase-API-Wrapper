import asyncio
import uuid
from datetime import datetime
from tabulate import tabulate
from coinbase.rest import RESTClient

class AsyncCoinbaseAPI:
    def __init__(self, api_key: str, api_secret: str, verbose: bool = False):
        """
        Initialize the AsyncCoinbaseAPI.

        Args:
            api_key (str): Coinbase API key.
            api_secret (str): Coinbase API secret.
            verbose (bool, optional): If True, enables task monitoring. Defaults to False.
        """
        self.client = RESTClient(api_key=api_key, api_secret=api_secret)

        self.tasks = []

        self.verbose = verbose
        if self.verbose:
            self.monitor_task = asyncio.create_task(self.monitor_tasks(refresh_interval=0.2))

    async def async_call(self, method_name: str, **kwargs):
        """
        Asynchronously call a method on the RESTClient instance.

        Args:
            method_name (str): Name of the method to call on the RESTClient instance.
            **kwargs: Keyword arguments to pass onto the method.

        Returns:
            Method call result or None if an exception occurs.
        """
        loop = asyncio.get_event_loop()
        method = getattr(self.client, method_name, None)

        if not method:
            raise AttributeError(f"Method '{method_name}' not found in RESTClient")

        task_id, timestamp = self.generate_task_id()

        async def wrapped_method():
            try:
                result = await loop.run_in_executor(None, lambda: method(**kwargs))
                return result, None
            except Exception as e:
                return None, type(e).__name__

        task = asyncio.create_task(wrapped_method())
        self.tasks.append((task, method_name, task_id, timestamp))

        return await task

    async def monitor_tasks(self, refresh_interval: int = 1):
        """
        Continuously prints a table with information about all tracked tasks to the console.

        Args:
            refresh_interval (float): Time in seconds to wait before refreshing the table.
        """
        try:
            while True:
                tasks_info = self.get_tasks_info()
                
                table = tabulate(tasks_info, headers="keys", tablefmt="grid")
                print("\033c", end="")  # Clear console (Linux/OSX)
                print(table)
                
                await asyncio.sleep(refresh_interval)
        except asyncio.CancelledError:
            pass

    async def close(self):
        """
        Waits for all tracked async tasks to complete, cancels monitoring if it is running, and clears resources.
        """
        tasks = [task for task, _, _, _ in self.tasks]
        
        if tasks:
            await asyncio.gather(*tasks)

        if self.verbose and hasattr(self, 'monitor_task'):
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        self.tasks.clear()
        print("All tasks completed and resources closed.")

    def get_tasks_info(self):
        """
        Returns a list of dictionaries with information about all tracked tasks.

        Returns:
            List[Dict]: List containing task information (task ID, method name, state, result, exception, timestamp).
        """
        tasks_info = []

        for task, method_name, task_id, timestamp in self.tasks:
            if task.done():
                result, exception = task.result()
                if exception:
                    result = "Error"
                else:
                    result = "Success"
            else:
                exception = "Pending"
                result = "Pending"
            
            task_info = {
                "timestamp": timestamp,
                "task_id": task_id,
                "method": method_name,
                "state": "completed" if task.done() else "running",
                "result": result,
                "exception": exception if exception else "None"
            }
            tasks_info.append(task_info)

        return tasks_info

    def generate_task_id(self):
        """
        Generates a unique task ID using UUID. Also passes down a timestamp indicating id creation datetime.

        Returns:
            Tuple[str, str]: Tuple containing a unique task ID and the creation timestamp.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        unique_id = uuid.uuid4().hex[:12]

        return unique_id, timestamp