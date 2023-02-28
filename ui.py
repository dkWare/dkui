from math import isclose, sqrt
from typing import overload
from numpy import clip
import arcade


def write_log(action, id, code):
    print(f"[{id}] <{code}> {action}")


class Vector2D:
    """
    This Class represents a simple two dimensional Vector
    It has two values:

     - a: float | int
     - b: float | int

    ## properties
    once created values can't be changed. It is immutable
    you can check that if its immutable by using:
     - @mutable
    you can get the values separate by using:
     - @valA for the content of a
     - @valB for the content of b
    or both in a tuple by using:
     - @values
    """
    def __init__(self, a: float, b: float):
        self._a = a
        self._b = b

    @property
    def mutable(self):
        return False

    @property
    def valA(self):
        return self._a

    @property
    def valB(self):
        return self._b

    @property
    def values(self):
        return self._a, self._b

Vector2D.__mro__


class MousePointer(Vector2D):
    """
    This Class represents the position off the Mouse
    It has two values:

     - a: float | int
     - b: float | int

    ## properties
    once created values can't be changed. It is mutable
    you can check that if its mutable by using:
     - mutable
    you can get the values separate by using:
     - @valA for the content of a
     - @valB for the content of b
    or both in a tuple by using:
     - @values
    ## methods
    you can use the change method to change a and b:
     - @change(new_a: float|int, new_b: float|int)
    """
    def __init__(self, a: float, b: float):
        super().__init__(a, b)

    @property
    def mutable(self):
        return True

    def change(self, a, b):
        self._a = a
        self._b = b


class UIManager:
    """
    This class is a shortcut to not have to use these methods on every single element.
    And for example to shorten 80 lines in 4 for 20 elements.

    ## register
    use the register method to regress single elements. You can also pass an instance of
    this manager either directly when creating the element from a predefined class or also
    pass an instance at super.__init__ for your own classes that inherit from one of the predefined
    classes. if you do one of the two above you don't have to use this method on the named object
    or on all created objects of this class.

    ## draw
    this method calls the function with the same name for all regressed elements

    ## update
    with this method the function with the same name is called for all regressed elements

    ## raise_click_event_press
    with this method the function with the same name is called for all regressed elements

    ## raise_click_event_release
    this method calls the function with the same name for all regressed elements

    ## getitem
    You can access individual elements by accessing them with their ID:
    gui_manager_object[element_id]
    """
    def __init__(self, mouse_pointer: MousePointer, *fields):
        self.field_list = []
        self.field_dict = {}
        for field in fields:
            self.field_list.append(field)
            self.field_dict[field.ID] = field
        self._mouse_pointer = mouse_pointer

    def register(self, field):
        """
        use the register method to regress single elements. You can also pass an instance of
        this manager either directly when creating the element from a predefined class or also
        pass an instance at super.__init__ for your own classes that inherit from one of the predefined
        classes. if you do one of the two above you don't have to use this method on the named object
        or on all created objects of this class.
        """
        field.register_mouse(self._mouse_pointer)
        self.field_list.append(field)
        self.field_dict[field.ID] = field

    def draw(self):
        """
        Draw all the elements
        For more details please refer to the same method in the respective element
        """
        for field in self.field_list:
            field.draw()

    def update(self):
        """
        Update all elements
        For more details please refer to the same method in the respective element
        """
        for field in self.field_list:
            field.update_field()

    def raise_click_event_press(self, button: int):
        """
        Trigger a mouse press event at each element
        For more details please refer to the same method in the respective element

        button: int the pressed button
        """
        for field in self.field_list:
            field.raise_click_event_press(button)

    def raise_click_event_release(self, button: int):
        """
        Trigger a mouse release event on each element
        For more details please refer to the same method in the respective element

        button: int the released button
        """
        for field in self.field_list:
            field.raise_click_event_release(button)

    def __getitem__(self, name):
        if name in self.field_dict:
            return self.field_dict[name]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

class UIField:
    def _create_point_list(self, pointA: Vector2D, pointB: Vector2D, pointC: Vector2D, pointD: Vector2D):
        """
        method to create the required point_list and point_list_raw

        Args:
            pointA (Vector2D): The point from the fields upper left
            pointB (Vector2D): The point from the fields upper right
            pointC (Vector2D): The point from the fields lower right
            pointD (Vector2D): The point from the fields lower left

        Returns:
            None
        """
        point_list = [pointA, pointB, pointC, pointD]
        if None in point_list:
            return
        self._point_list_raw = [point.values for point in point_list]
        self._point_list = point_list

    def _init_values(self, id: str):
        """
        In this method all flags and the required data for the button
        are set to default for later use. They can always be changed after creation

        Args:
            id (str): The ID of this field for debug uses

        Returns:
            None
        """
        #for debug uses
        self._id = id
        self.debug = True

        #Mouse Event flags
        self._mouse_press_on_field = False
        self._mouse_pointer_in_field = False
        self.release_event_outside_field = True
        self._mouse_click_logic_overwrite = False

        #Visual Flags and colors
        self._mouse_click_visual_overwrite = False
        self._color_masked = arcade.color.DARK_GREEN
        self._color_unmasked = arcade.color.RED
        self._color_pressed = arcade.color.GREEN
        self._color_field_locked = arcade.color.DARK_RED

        #Control flags Events, Logic and Visual
        self._field_active = True
        self._field_visible = True
        self._field_locked = False
        self._listen_for_mouse_enter_event = True
        self._listen_for_mouse_leave_event = True

        #Create Mouse Pointer Var for IDE
        #Check if its not already exists
        #so that it wont overwrite in future
        #cases
        if not hasattr(self, "_mouse_pointer"):
            self._mouse_pointer = None

    def register_mouse(self, mouse: MousePointer):
        """
        Register a mouse for all events that need mouse position.
        for example entering or leaving the field with it.

        Args:
            mouse (MousePointer): An instance off the MousePointer class
        """
        self._mouse_pointer = mouse

    def _try_register(self, ui_manager: UIManager):
        if ui_manager:
            ui_manager.register(self)

    def __init__(self, id: str=None, *, pointA: Vector2D=None, pointB: Vector2D=None, pointC: Vector2D=None, pointD: Vector2D=None, ui_manager: UIManager=None, other_form:bool=False):
        """
        Create the default UIField. Its shape is a Rectangle, to create it you need to give four points and ab id for debugging.
        If you want that the Field registers automatically you can also give an instance from the class UIManager.

        Args:
            id (str): The ID of this field for debug uses
            pointA (Vector2D): The point from the fields upper left
            pointB (Vector2D): The point from the fields upper right
            pointC (Vector2D): The point from the fields lower right
            pointD (Vector2D): The point from the fields lower left
            ui_manager (UIManager, optional): If you want to register it automatically. Defaults to None.
            other_form (bool, optional): This is used internal. Defaults to False.
        """
        if other_form:
            return
        self._create_point_list(pointA, pointB, pointC, pointD)
        self._init_values(id)
        self._try_register(ui_manager)

    @classmethod
    def init_other_shape(cls, id: str, *, ui_manager: UIManager=None):
        """
        Use this if you want to create a UIField thats
        shaped differently then a Rectangle.
        Here you only need the id. You can also give an instance of
        the UIManager class to register it.

        Args:
            id (str): The ID of this field for debug uses
            ui_manager (UIManager, optional): If you want to register it automatically. Defaults to None.
        """
        field = cls(other_form=True)
        field._init_values(id)
        field._try_register(ui_manager)
        return field

    def _position_over_field(self, position: Vector2D, *, pointA: Vector2D, pointC: Vector2D):
        """
        This method detects if the given position is in the given area/field

        Args:
            position (Vector2D): The given position given as Vector2D or MousePointer
            pointA (Vector2D): _description_
            pointC (Vector2D): _description_

        Returns:
            bool True if the mouse is in the field
        """
        if not pointA.valA <= position.valA <= pointC.valA:
            return False

        if not pointC.valB <= position.valB <= pointA.valB:
            return False

        return True

    def _get_flag_change(self, oldFlagState: bool, newFlagState: bool):
        """
        Shows the change from an old state to the new state of an given Flag

        Args:
            oldFlagState (bool): The old value off the Flag
            newFlagState (bool): The new value off the Flag

        Returns:
            tuple[bool, bool]
            False, False: Nothing has changed
            False, True: The value has gone from False to True
            True, False: The value has gone from True to False
        """
        if oldFlagState == 0 and newFlagState == 1:
            return False, True
        if oldFlagState == 1 and newFlagState == 0:
            return True, False
        return False, False

    def update_field(self):
        """
        Update the UIField, check if active and not locked.
        If both is correct call the on_update method then checks if
        the mouse has entered or left the field.
        if it has entered call the on_mouse_enters and if the mouse has left call
        the on_mouse_leaves method
        """
        if not self._field_active:
            return

        if self._field_locked:
            return

        self.on_update()

        new_mouse_pointer_in_field = self._position_over_field(self._mouse_pointer, pointA=self._point_list[0], pointC=self._point_list[2])

        mouse_leaves_field, mouse_enters_field = self._get_flag_change(self._mouse_pointer_in_field, new_mouse_pointer_in_field)

        if mouse_enters_field and self._listen_for_mouse_enter_event:
            if self.debug: write_log("mouse enters field", self._id, 100)
            self.on_mouse_enters()

        if mouse_leaves_field and self._listen_for_mouse_leave_event:
            if self.debug: write_log("mouse leaves field", self._id, 100)
            self.on_mouse_leaves()

        self._mouse_pointer_in_field = new_mouse_pointer_in_field

    def draw(self):
        """
        Draws the Field
        """
        if not self._field_visible:
            return

        if self._field_locked:
            color = self._color_field_locked
        elif self._mouse_press_on_field:
            color = self._color_pressed
        else:
            color = self._color_unmasked if not self._mouse_pointer_in_field and not self._mouse_click_visual_overwrite else self._color_masked
        arcade.draw_polygon_filled(self._point_list_raw, color)

        if not self.debug:
            return

        for index, point in enumerate(self._point_list):
            arcade.draw_text(index, *point.values)

    def raise_click_event_press(self, button: int):
        """
        Aktualisiert den Zustand des Feldes basierend auf der Maus-Eingabe.

        Prüft, ob der Mauszeiger sich innerhalb des Feldes befindet und ruft bei
        einem Mausklick die `on_button_press` Methode auf.

        Args:
            button (int): Die Nummer des Mausklicks.

        Returns:
            None
        """
        if not self._field_active:
            return

        if self._field_locked:
            return

        if self._mouse_pointer_in_field:
            if self.debug: write_log(f"mouse press field: {button}", self._id, 100)
            self._mouse_press_on_field = True
            self.on_button_press(button)

    def raise_click_event_release(self, button: int):
        """
        Aktualisiert den Zustand des Feldes basierend auf der Maus-Eingabe.

        Prüft, ob der Mauszeiger sich innerhalb des Feldes befindet und ruft bei
        einem Mausklick die `on_button_press` Methode auf.

        Args:
            button (int): Die Nummer des Mausklicks.

        Returns:
            None
        """
        if not self._field_active:
            return

        if self._field_locked:
            return

        release_event_overwrite = False

        if self.release_event_outside_field and self._mouse_press_on_field:
            release_event_overwrite = True

        if self._mouse_pointer_in_field or release_event_overwrite:
            if self.debug: write_log(f"mouse release field: {button}", self._id, 100)
            self.on_button_release(button)
            self._mouse_press_on_field = False

    def on_mouse_enters(self):
        """
        Diese Methode wird aufgerufen, wenn der Mauszeiger in das UI-Element eintritt.
        """

    def on_mouse_leaves(self):
        """
        Diese Methode wird aufgerufen, wenn der Mauszeiger das UI-Element verlässt.
        """

    def on_button_press(self, button):
        """
        Diese Methode wird aufgerufen, wenn eine Maustaste auf dem UI-Element gedrückt wird.

        Parameter:
        -----------
        button: int
            Die ID der gedrückten Maustaste.
        """

    def on_button_release(self, button):
        """
        Diese Methode wird aufgerufen, wenn eine Maustaste auf dem UI-Element gedrückt wird.

        Parameter:
        -----------
        button: int
            Die ID der gedrückten Maustaste.
        """

    def on_unlock(self):
        """UNLOCK"""

    def on_lock(self):
        """LOCK"""

    def on_activate(self):
        """ACTIVATE"""

    def on_deactivate(self):
        """DEACTIVATE"""

    def on_hide(self):
        """HIDE"""

    def on_visible(self):
        """VISIBLE AGAIN"""

    def on_update(self):
        """
        Diese Methode wird vor jedem update aufgerufen wenn das feld active ist und nicht gelocked
        """

    def activate(self):
        self._field_visible = True
        self._field_active = True
        self.on_activate()

    def deactivate(self):
        self._field_visible = False
        self._field_active = False
        self.on_deactivate()

    def set_visible(self, x: bool):
        show, hide = self._get_flag_change(self._field_visible, x)
        if hide:
            self.on_hide()
        else:
            self.on_visible()
        self._field_visible = x

    def set_active(self, x: bool):
        deactivate, activate = self._get_flag_change(self._field_active, x)
        if activate:
            self.on_activate()
        else:
            self.on_deactivate()
        self._field_active = x

    def set_locked(self, x: bool):
        unlock, lock = self._get_flag_change(self._field_locked, x)
        if lock:
            if self.debug: write_log("field locked", self._id, 100)
            self.on_lock()
        else:
            if self.debug: write_log("field unlocked", self._id, 100)
            self.on_unlock()
        self._field_locked = x
        if x:
            self._mouse_pointer_in_field = False
            self._mouse_press_on_field = False

    def set_color_unmasked(self, color: arcade.color):
        self._color_unmasked = color

    def set_color_masked(self, color: arcade.color):
        self._color_masked = color

    def set_color_pressed(self, color: arcade.color):
        self._color_pressed = color

    def set_color_locked(self, color: arcade.color):
        self._color_field_locked = color

    def overwrite_visual_mouse_click(self, x: bool):
        self._mouse_click_visual_overwrite = x

    def listen_for_mouse_enter(self, x: bool):
        self._listen_for_mouse_enter_event = x

    def listen_for_mouse_leaving(self, x: bool):
        self._listen_for_mouse_leave_event = x

    def raise_mouse_move_events(self, x: bool):
        self._listen_for_mouse_enter_event = x
        self._listen_for_mouse_leave_event = x

    @property
    def IS_ACTIVE(self):
        return self._field_active and self._field_visible

    @property
    def IS_VISIBLE(self):
        return self._field_visible

    @property
    def IS_LOCKED(self):
        return self._field_locked

    @property
    def ID(self):
        return self._id

    @property
    def MOUSE(self):
        return self._mouse_pointer

    def __str__(self) -> str:
        if not self.debug:
            return ""
        points = ""
        for point in self._point_list_raw:
            points += " " + str(point)
        return f"{self._id}: {self._point_list_raw[1][0] - self._point_list_raw[0][0]} : {self._point_list_raw[3][1] - self._point_list_raw[0][1]}\n{points}"


class RectButton(UIField):
    def set_field(self, *, width: float=None, height: float=None, center_x: float=None, center_y: float=None, text_dx: float=None, text_dy: float=None):
        old_x = self._centerPos.valA
        old_y = self._centerPos.valB

        if width is None:
            width = self._width
        if height is None:
            height = self._height
        if center_x is None:
            center_x = self._center_x
        if center_y is None:
            center_y = self._center_y
        if text_dx is None:
            text_dx = self._text_dx
        if text_dy is None:
            text_dy = self._text_dy

        half_width = width/2
        half_height = height/2

        point_a = Vector2D(center_x-half_width, center_y)
        point_b = Vector2D(center_x+half_width, center_y)
        point_c = Vector2D(center_x+half_width, center_y-half_height)
        point_d = Vector2D(center_x-half_width, center_y-half_height)
        self._create_point_list(point_a, point_b, point_c, point_d)

        self._text_x = center_x-half_width+text_dx
        self._text_y = center_y-half_height+text_dy

        self._centerPos = Vector2D(center_x, center_y)

        dx = old_x - center_x
        dy = old_y - center_y

        if dx != 0 or dy != 0:
            self.on_position_change(self._centerPos)


    def __init__(self, id: str, *, center_x: float, center_y: float, width: float, height: float, text: str, text_size: int, text_dx: float, text_dy: float, ui_manager: UIManager=None, release_event_outside_field:bool=False):
        self._center_x = center_x
        self._center_y = center_y
        self._width = width
        self._height = height
        self._text_dx = text_dx
        self._text_dy = text_dy

        half_width = width/2
        half_height = height/2

        point_a = Vector2D(center_x-half_width, center_y)
        point_b = Vector2D(center_x+half_width, center_y)
        point_c = Vector2D(center_x+half_width, center_y-half_height)
        point_d = Vector2D(center_x-half_width, center_y-half_height)
        super().__init__(id, pointA=point_a, pointB=point_b, pointC=point_c, pointD=point_d)

        self._text_x = center_x-half_width+text_dx
        self._text_y = center_y-half_height+text_dy

        self.text = text
        self._text_size = text_size

        self._centerPos = Vector2D(center_x, center_y)
        self._size = Vector2D(width, height)

        if ui_manager:
            ui_manager.register(self)

    def draw(self):
        if not self._field_visible:
            return

        super().draw()
        arcade.draw_text(self.text, self._text_x, self._text_y, font_size=self._text_size)

    def on_position_change(self, new_position: Vector2D):
        """Diese Methode wird bei änderung der posiotion aufgerufen"""


class UIFieldCircle(UIField):
    def __init__(self, id: str, *, centerPos: Vector2D, radius: float, ui_manager: UIManager=None):
        super().__init__(id)

        if ui_manager:
            ui_manager.register(self)

        self._centerPos = centerPos
        self._radius = radius


    def inArea(self, position: Vector2D, center: Vector2D, radius: float):
        dx = position.valA - center.valA
        dy = position.valB - center.valB
        distance = sqrt(dx**2 + dy**2)
        if distance > radius:
            return False
        return True

    def detectChange(self, old: bool, new: bool):
        if old == 0 and new == 1:
            return False, True
        if old == 1 and new == 0:
            return True, False
        return False, False

    def update(self, mouse: MousePointer):
        new_mouse_pointer_in_field = self.inArea(mouse, self._centerPos, self._radius)

        mouse_leaves_field, mouse_enters_field = self.detectChange(self._mouse_pointer_in_field, new_mouse_pointer_in_field)

        if mouse_enters_field:
            if self.debug: write_log("mouse enters field", self._id, 100)
            self.on_mouse_enters()

        if mouse_leaves_field:
            if self.debug: write_log("mouse leaves field", self._id, 100)
            self.on_mouse_leaves()

        self._mouse_pointer_in_field = new_mouse_pointer_in_field

    def draw(self):
        color = self._color_unmasked if not self._mouse_pointer_in_field else self._color_masked
        arcade.draw_circle_filled(self._centerPos.valA, self._centerPos.valB, self._radius, color)


class CircleButton(UIFieldCircle):
    def __init__(self, id: str, *, center_x: float, center_y: float, radius: float, text: str, text_size: int, text_dx: float, text_dy: float, color_masked: arcade.Color, color_unmasked: arcade.Color, ui_manager: UIManager=None):
        super().__init__(id, centerPos=Vector2D(center_x, center_y), radius=radius)

        self._color_masked = color_masked
        self._color_unmasked = color_unmasked

        self._text = text

        self._text_x = center_x-text_dx
        self._text_y = center_y-text_dy
        self._text_size = text_size

        if ui_manager:
            ui_manager.register(self)


    def draw(self):
        super().draw()
        arcade.draw_text(self._text, self._text_x, self._text_y, font_size=self._text_size)


class TextureButtom(RectButton):
    def __init__(self, id: str, *, center_x: float, center_y: float, width: float, height: float, text: str, text_size: int, text_dx: float, text_dy: float, texture_masked: str, texture_unmasked: str, scale: float, ui_manager: UIManager=None):
        super().__init__(id, center_x=center_x, center_y=center_y, width=width, height=height, text=text, text_size=text_size, text_dx=text_dx, text_dy=text_dy, color_masked=None, color_unmasked=None)

        self._texture_unmasked = arcade.load_texture(texture_unmasked)
        self._texture_masked = arcade.load_texture(texture_masked)

        if ui_manager:
            ui_manager.register(self)

    def draw(self):
        texture = self._texture_unmasked if not self._mouse_pointer_in_field else self._texture_masked
        arcade.draw_texture_rectangle(self._centerPos.valA, self._centerPos.valB, self._size.valA, self._size.valB, texture)

        if not self.debug:
            return

        for index, point in enumerate(self._point_list):
            arcade.draw_text(index, *point.values)