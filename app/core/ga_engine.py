# ga_engine.py - Genetic Algorithm สำหรับหาชุดไอเทมที่ดีที่สุด
import random
from typing import List, Dict, Tuple
from app.core.evaluator import BuildEvaluator
from app.config import GA_SETTINGS

class GeneticEngine:
    """
    Engine สำหรับรัน Genetic Algorithm
    ใช้หลักการวิวัฒนาการเพื่อหา build ที่ดีที่สุดสำหรับ hero
    """
    
    def __init__(self, evaluator: BuildEvaluator, valid_item_ids: List[int], ga_settings: Dict = None):
        self.evaluator = evaluator
        self.item_pool = valid_item_ids
        
        settings = ga_settings if ga_settings else GA_SETTINGS
        self.pop_size = settings['POP_SIZE']
        self.mutation_rate = settings['MUTATION_RATE']
        self.max_gen = settings['MAX_GEN']
        self.elitism_count = settings['ELITISM_COUNT']

    def create_chromosome(self) -> List[int]:
        """สุ่ม build ใหม่ (6 ไอเทมไม่ซ้ำ)"""
        if len(self.item_pool) >= 6:
            return random.sample(self.item_pool, 6)
        return random.choices(self.item_pool, k=6)
    
    def ensure_unique_items(self, chromosome: List[int]) -> List[int]:
        """แก้ไข build ที่มีไอเทมซ้ำ"""
        seen = set()
        result = []
        for item_id in chromosome:
            if item_id not in seen:
                result.append(item_id)
                seen.add(item_id)
            else:
                available = [i for i in self.item_pool if i not in seen]
                if available:
                    new_item = random.choice(available)
                    result.append(new_item)
                    seen.add(new_item)
                else:
                    result.append(item_id)
        return result

    def crossover(self, parent1: List[int], parent2: List[int]) -> List[int]:
        """ผสม build จาก 2 parents"""
        point = random.randint(1, 5)
        child = parent1[:point] + parent2[point:]
        return self.ensure_unique_items(child)

    def mutate(self, chromosome: List[int]) -> List[int]:
        """สุ่มเปลี่ยนไอเทม 1 ชิ้น"""
        if random.random() < self.mutation_rate:
            idx = random.randint(0, 5)
            available = [i for i in self.item_pool if i not in chromosome]
            if available:
                chromosome[idx] = random.choice(available)
        return chromosome

    def run(self) -> Tuple[List[int], float]:
        """รัน GA และ return build ที่ดีที่สุด"""
        population = [self.create_chromosome() for _ in range(self.pop_size)]
        
        best_solution = []
        best_fitness = -999999.0
        
        for gen in range(self.max_gen):
            # ประเมิน fitness ของทุกตัว
            scores = [(chrom, self.evaluator.get_fitness(chrom)) for chrom in population]
            scores.sort(key=lambda x: x[1], reverse=True)
            
            # เก็บตัวที่ดีที่สุด
            if scores[0][1] > best_fitness:
                best_fitness = scores[0][1]
                best_solution = scores[0][0][:]

            # สร้าง generation ถัดไป
            next_gen = [s[0][:] for s in scores[:self.elitism_count]]  # elites
            
            while len(next_gen) < self.pop_size:
                parent1 = random.choice(scores[:10])[0]
                parent2 = random.choice(scores[:10])[0]
                child = self.crossover(parent1[:], parent2[:])
                child = self.mutate(child)
                next_gen.append(child)
                
            population = next_gen
            
        return best_solution, best_fitness