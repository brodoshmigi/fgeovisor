from abc import ABC, abstractmethod


class DataLoader:

    @abstractmethod
    def download_image(self) -> None: pass

    @abstractmethod
    def calculate_index(self) -> None: pass

    @abstractmethod
    def auth(self) -> None: pass

    @abstractmethod
    def load_data(self) -> None: pass
