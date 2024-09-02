# project: p3
# submitter: hhess3
# partner: none
# hours: 12

from collections import deque
import os
import pandas as pd
import time
import requests 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def visit_and_get_children(self, node):
        """ Record the node value in self.order, and return its children
        param: node
        return: children of the given node
        """
        self.order.append(node) 
    
        raise Exception("must be overridden in sub classes -- don't change me here!")
        return self.children
      

    def dfs_search(self, node):
        # 1. clear out visited set and order list
        self.visited.clear()
        self.order.clear()
        # 2. start recursive search by calling dfs_visit
        self.dfs_visit(node)

    def dfs_visit(self, node):
        # 1. if this node has already been visited, just `return` (no value necessary)
        if node in self.visited:
            return 
        
        self.visited.add(node) 
        
        children = self.visit_and_get_children(node)
        
        for child in children:
            self.dfs_visit(child)
            
    def bfs_search(self, node):
        self.visited.clear()
        self.order.clear()
        to_visit = deque([node])
        
        while to_visit:
            current_node = to_visit.popleft()
            if current_node in self.visited:
                continue
            
            self.visited.add(current_node)
            children = self.visit_and_get_children(current_node)
            
            for child in children:
                if child not in self.visited:
                    to_visit.append(child)            
            
class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__() # call constructor method of parent class
        self.df = df

    def visit_and_get_children(self, node):
        # TODO: Record the node value in self.order
        self.order.append(node)
        children = []
        # TODO: use `self.df` to determine what children the node has and append them
        for child, has_edge in self.df.loc[node].items():
            if has_edge:
                children.append(child)
                      
        return children
    
    
class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()

    def visit_and_get_children(self, node):
        node_path = os.path.join("file_nodes", node)
        if os.path.isfile(node_path):
            with open(node_path, 'r') as file:
                lines = file.readlines()
                value = lines[0].strip()
                children = lines[1].strip().split(',')
        else:
            children = []
            value = None
            with open(node_path, 'r') as file:
                children = file.readlines()
                children = [child.strip() for child in children]
        self.order.append(value if value else os.path.basename(node))

        return children

    def concat_order(self):
        return ''.join(self.order)
    
class WebSearcher(GraphSearcher):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.tables = []  
        
    def visit_and_get_children(self, url):
        self.driver.get(url)
        self.order.append(url)
        links = self.driver.find_elements("tag name",'a')
        urls = [link.get_attribute('href') for link in links if link.get_attribute('href')]
        
        tables = pd.read_html(self.driver.page_source)
        self.tables.extend(tables)
        
        return urls

    def table(self):
        dataframes = []
        headers = ["clue", "latitude", "longitude", "description"]
        for table_data in self.tables:
            df = pd.DataFrame(table_data)
            if set(headers).issubset(df.columns):
                dataframes.append(df[headers])
        return pd.concat(dataframes, ignore_index=True)
    

def reveal_secrets(driver, url, travellog):
    first_str = ""
    for i in travellog["clue"]:
        first_str += str(i)
    password = first_str
    driver.get(url)
    automated_password = driver.find_element(By.ID, "password-textbox")
    automated_password
    automated_password.clear()
    automated_password.send_keys(password)
    button = driver.find_element(By.ID, "submit-button")
    button.click()
    
    time.sleep(5)
    
    view_location_button = driver.find_element(By.ID, "view-location-button") 
    view_location_button.click()
    
    time.sleep(8)  
    
    image_element = driver.find_element(By.ID, "image") 
    image_url = image_element.get_attribute('src')
    
    image_response = requests.get(image_url)
    with open('Current_Location.jpg', 'wb') as f:
        f.write(image_response.content)
    
    location_element = driver.find_element(By.ID, "location")  
    current_location = location_element.text
    
    return current_location







    
    
