# app/core/ga_engine.py
import random
from typing import List, Dict, Tuple
from app.core.evaluator import BuildEvaluator
from app.config import GA_SETTINGS

class GeneticEngine:
    def __init__(self, evaluator: BuildEvaluator, valid_item_ids: List[int]):
        self.evaluator = evaluator
        self.item_pool = valid_item_ids
        self.pop_size = GA_SETTINGS['POP_SIZE']
        self.mutation_rate = GA_SETTINGS['MUTATION_RATE']
        self.max_gen = GA_SETTINGS['MAX_GEN']

    def create_chromosome(self) -> List[int]:
        """สุ่มไอเทม 6 ชิ้นจาก Pool"""
        return [random.choice(self.item_pool) for _ in range(6)]

    def crossover(self, parent1: List[int], parent2: List[int]) -> List[int]:
        """ผสมพันธุ์แบบ Single Point Crossover"""
        point = random.randint(1, 5)
        child = parent1[:point] + parent2[point:]
        return child

    def mutate(self, chromosome: List[int]) -> List[int]:
        """กลายพันธุ์: เปลี่ยนของ 1 ชิ้นเป็นอย่างอื่น"""
        if random.random() < self.mutation_rate:
            idx = random.randint(0, 5)
            chromosome[idx] = random.choice(self.item_pool)
        return chromosome

    def run(self) -> Tuple[List[int], float]:
        """รัน GA Loop"""
        # 1. Init Population
        population = [self.create_chromosome() for _ in range(self.pop_size)]
        
        best_solution = []
        best_fitness = -999999.0
        
        for generation in range(self.max_gen):
            # 2. Evaluate Fitness
            scores = [(chrom, self.evaluator.get_fitness(chrom)) for chrom in population]
            
            # Sort หาตัวเก่งสุดในรุ่น
            scores.sort(key=lambda x: x[1], reverse=True)
            
            current_best_chrom, current_best_score = scores[0]
            if current_best_score > best_fitness:
                best_fitness = current_best_score
                best_solution = current_best_chrom
            
            # (Optional: Print progress)
            # if generation % 10 == 0:
            #     print(f"Gen {generation}: Best Score {best_fitness:.2f}")

            # 3. Selection (Elitism + Tournament)
            next_gen = []
            
            # เก็บตัวเทพไว้ (Elitism)
            elites = [s[0] for s in scores[:GA_SETTINGS['ELITISM_COUNT']]]
            next_gen.extend(elites)
            
            # สร้างลูกหลาน
            while len(next_gen) < self.pop_size:
                # Tournament Selection แบบง่าย
                parent1 = random.choice(scores[:10])[0] # เลือกจาก Top 10
                parent2 = random.choice(scores[:10])[0]
                
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                next_gen.append(child)
                
            population = next_gen
            
        return best_solution, best_fitness