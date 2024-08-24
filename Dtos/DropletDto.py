class DropletDto:
    def __init__(self, image_filepath, volume, timestamp, seconds, center, radius, area):
        self.image_filepath = image_filepath
        self.volume = volume
        self.timestamp = timestamp
        self.seconds = seconds
        self.center = center
        self.radius = radius
        self.area = area

    def __repr__(self):
        return (f"DropletDto(first_number={self.volume}, timestamp={self.timestamp}, "
                f"center={self.center}, radius={self.radius}, area={self.area})")