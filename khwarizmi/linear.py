"""Linear class and specific linear types defined with its methods and attributes."""

import matplotlib.pyplot as plt

from khwarizmi.equations import Equation
from khwarizmi.exc import (InvalidFormError, LinearSolutionError,
                           RedundantConversionError, UnableToDefineFormError, UnsuitableSlopeInterceptForm, InfinitelySolutionsError)
from khwarizmi.misc import if_assign, exc_assign, num


class Linear(Equation):
    """Base class for all linear equations."""

    def __init__(self, equation):
        Equation.__init__(self, equation)
        self.equal_index = self.equation.index("=")
        self.form = self.get_form()
        self.x_mult = self.get_x_multiplier()
        self.y_mult = self.get_y_multiplier()
        self.slope = self.get_slope()
        self.y_intercept = num(self.solve_for("x", 0))

    def get_x_multiplier(self):
        """Returns whatever number is multiplying the x variable on this equation as a string."""

        side = if_assign(self.form == 'Standard Form', self.equation, self.sol_side)

        if side[0] == '-':
            multiplier = if_assign(side[1].isdigit(), self.get_number(side[1], 1, side), "1")
            return '-' + multiplier
        if side[0].isdigit():
            multiplier = self.get_number(side[0], 0, side)
        else:
            multiplier = 1

        return multiplier

    def get_y_multiplier(self):
        """Returns whatever number is multiplying the y variable on this equation"""

        eqtn, index = self.equation, self.equation.index('x') + 2

        if self.form == 'Standard Form':
            multiplier = if_assign(eqtn[index].isdigit(), self.get_number(eqtn[index], index), "1")

            if eqtn[index - 1] == '-':
                multiplier = '-' + multiplier
        else:
            if eqtn[0] == '-':
                multiplier = if_assign(eqtn[1].isdigit(), self.get_number(eqtn[1], 1), "1")
                multiplier = '-' + multiplier
            else:
                multiplier = if_assign(eqtn[0].isdigit(), self.get_number(eqtn[0], 0), "1")

        return multiplier

    def express_as(self, form):
        """Expresses the equation in the form passed as an argument
        and returns an instance of that form's class as the new expression.

        Valid forms are Slope-Intercept, Standard and Point-Slope.
        Keyword arguments:

        form (str): the form the equation will be converted to"""

        if self.form == "Slope-Intercept Form":
            return SlopeIntercept(self.equation).express_as(form)
        if self.form == "Standard Form":
            return Standard(self.equation).express_as(form)
        if self.form == "Point-Slope Form":
            return PointSlope(self.equation).express_as(form)

        return None

    def get_slope(self):
        """Returns the slope of this linear equation."""

        a_points, b_points = self.get_point(1), self.get_point(2)
        return num((a_points[1] - b_points[1]) / (a_points[0] - b_points[0]))

    def get_form(self):
        """ Returns the form of this linear equation."""

        if "x" in self.inc_side and "y" in self.inc_side:
            return "Standard Form"
        if self.equation[self.equal_index - 1] == "y":
            return "Slope-Intercept Form"
        if self.inc_side[0] == "y" and self.equation[self.equal_index - 1].isdigit():
            return "Point-Slope Form"

        raise UnableToDefineFormError(self.equation)

    def points(self, a, b):
        """Returns the points formed by all values of x between a and b.

        Keyword Arguments:

        a (int): initial value of the iteration.
        b (int): last value of the iteration.
        """

        solutions = []

        for i in range(a, b + 1):
            solutions.append(tuple((i, self.solve_for("x", i))))

        return solutions

    def get_point(self, x_value):
        """Returns the point formed when x is equal to x_value.

        Keyword arguments:

        x_value (int): the value of x the equation will be evaluated with to return
        the point."""

        # Confusing, uh? Returns, as a tuple, the value of x and the resulting
        # value of y.

        return tuple((x_value, self.solve_for("x", x_value)))

    def graph(self, points, y_label="", x_label=""):
        """Graphs the line formed by points.

        Keyword arguments:

        points (list of tuples): the points that define the line.

        y_label (str): label to describe the y axis (optional)

        x_label (str): label to describe the x axis (optional)"""

        x, y = [], []

        x.extend((points[0][0], points[-1][0]))
        y.extend((points[0][1], points[-1][1]))

        plt.plot(x, y)
        plt.ylabel(y_label)
        plt.xlabel(x_label)

        plt.show()

    def solve(self, show=False):
        """Overwritten solve() method inherited from Equation class
        to raise error if used on Linear class."""

        raise LinearSolutionError()

    def sort(self, for_variable):
        """Sorts this equation depending on its type to be solved
        for the variable argument.

        Keyword arguments:

        for_variable (str): the variable to sort the equation for."""

        if self.form == "Point-Slope Form":
            return PointSlope(self.equation).sort(for_variable)
        if self.form == "Slope-Intercept Form":
            return SlopeIntercept(self.equation).sort(for_variable)

        return Standard(self.equation).sort(for_variable)

    def show_sorted(self, variable, value, sol_side):
        """Shows the side pass as parameter sorted for the equation variable.

        Keyword arguments:

        variable (str): the variable to show the equation sorted for.

        value (int): the value that will replace the variable we are sorting for.

        sol_side: the side of the equation that was sorted (the solution side)."""

        if variable is self.incognitos[0]:
            inc = self.incognitos[1]
        else:
            inc = self.incognitos[0]

        print(inc + "=" + sol_side.replace(variable, value))

    def solve_for(self, variable, value, show=False):
        """Solves the equation after changing variable into value.

        Keyword Arguments:

        variable (str): the variable to be replaced by a value.
        value (int): the value to replace the variable by.
        (optional) show (bool) : print the sorted equation."""

        eqtn, value = self.equation, str(value)
        sol_side = self.sort(variable)

        if eqtn[eqtn.find(variable) - 1] == "(" and self.form != "Point-Slope Form":
            eqtn = eqtn.replace("(" + variable, "*(" + variable)
            sol_side = eqtn[eqtn.find("=") + 1:]

        if show is True:
            self.show_sorted(variable, value, sol_side)

        return num(eval(sol_side.replace(variable, value)))


class SlopeIntercept(Linear):
    """Class for linear equations of Slope-Intercept form."""

    def __init__(self, equation):
        self.equation = equation
        Linear.__init__(self, equation)
        self.warn_if_unsuitable()

    def __str__(self):
        return self.equation

    def warn_if_unsuitable(self):
        """Raises an error on initialization if equation is not fit."""

        if self.equation[self.equation.find('x') - 1] == "(":
            raise UnsuitableSlopeInterceptForm(self.equation)
        if any(char.isdigit() for char in self.inc_side):
            raise UnsuitableSlopeInterceptForm(self.equation)

    def sort_for_x(self):
        """Sorts equation for x."""

        eqtn, sol_side, y_mult = self.equation, self.sol_side, self.y_mult
        x_index = eqtn.index('x')

        # Set the solution side
        sol_side = "(" + sol_side + ")/" + y_mult
        # Add a * symbol before the x if there's a number before it.
        sol_side = if_assign(eqtn[x_index - 1].isdigit(), sol_side.replace('x', '*x'), sol_side)
        # Beautify the solution side.
        sol_side = Equation.beautify(sol_side)

        return sol_side

    def sort_for_y(self):
        """Sorts equation for y."""

        eqtn, sol_side = self.equation, self.sol_side
        x_index = eqtn.index('x')
        operator = if_assign(eqtn[x_index + 1] == '-', '+', '-')
        slope_sign = if_assign(eqtn[0] == '-', '-', '')

        sol_side = "(" + self.y_mult + "*y" + operator + \
                   str(self.y_intercept).replace('-', '') + ")/" + slope_sign + str(self.slope)
        sol_side = Equation.beautify(sol_side)

        return sol_side


    def sort(self, for_variable):
        """Sorts a Slope-Intercept Form linear equation
        to be solved for a given variable.

        Keyword arguments:

        variable(str) : the variable this equation will be sorted to solve for."""

        # Sorts everything to solve for x.
        if for_variable == 'x':
            return self.sort_for_x()

        # Sorts everything to solve for y.
        return self.sort_for_y()

    def express_as(self, form):
        """Expresses the equation in the form passed as an argument
        and returns an instance of that form's class as the new expression.

        Valid forms are Slope-Intercept, Standard and Point-Slope.
        Keyword arguments:

        form (str): the form the equation will be converted to"""

        # Required and convenient variables definition.

        forms = ["Slope-Intercept", "Point-Slope", "Standard"]
        slope, y_intercept = str(self.slope), str(self.y_intercept)

        if form not in forms:
            raise InvalidFormError(form, forms)
        if form in self.form:
            raise RedundantConversionError(form)

        # Express in Standard Form.
        if form == "Standard":

            slope = slope.replace('-', '')
            x_op = if_assign(self.slope < 0, '', '-')

            # 'y' will always be positive, for negative multipliers of it will
            # be distributed. Hence why '+' is the operator before 'y'.

            rewritten = x_op + slope + "x" + '+' + "y" + "=" + y_intercept
            rewritten = Equation.beautify(rewritten)

            return Standard(rewritten)

        # Express in Point-Slope form.
        if form == "Point-Slope":

            points = self.get_point(2)
            x_point, y_point = str(points[0]), str(points[1])

            rewritten = "y-" + y_point + "=" + slope + "(x-" + x_point + ")"
            rewritten = Equation.beautify(rewritten)

            return PointSlope(rewritten)

        raise InvalidFormError(form, forms)


class Standard(Linear):
    """Class for linear equations of Standard Form."""

    def __init__(self, equation):
        Linear.__init__(self, equation)

    def __str__(self):
        return self.equation

    def sort(self, for_variable):
        """Sorts a Standard Form linear equation
        to be solved for a given variable.

        Keyword arguments:

        variable (str): the variable this equation will be sorted to solve for."""

        # Required and convenient variables definition.

        eqtn = self.equation
        c_pos, a, b = eqtn.find("=") + 1, self.x_mult, self.y_mult
        c = self.get_number(eqtn[c_pos], c_pos)
        den = if_assign(for_variable == 'y', a, b)
        mult = if_assign(for_variable == 'y', b, a)

        if eqtn[eqtn.index(for_variable) - len(str(mult)) - 1] == "-":
            operator = "+"
        else:
            operator = "-"

        # Expressing

        sol_side = "(" + c + operator + mult + "*" + for_variable + ")" + "/" + den
        sol_side = Equation.beautify(sol_side)

        return sol_side

    def express_as(self, form):
        """Expresses the equation in the form passed as an argument
        and returns an instance of that form's class as the new expression.

        Valid forms are Slope-Intercept, Standard and Point-Slope.
        Keyword arguments:

        form (str): the form the equation will be converted to"""

        slope = str(self.slope)
        forms = ["Slope-Intercept", "Point-Slope", "Standard"]

        if form not in forms:
            raise InvalidFormError(form, forms)
        if form in self.form:
            raise RedundantConversionError(form)

        if form == "Point-Slope":

            points = self.get_point(2)
            x_point, y_point = str(points[0]), str(points[1])
            rewritten = "y-" + y_point + "=" + slope + "(x-" + x_point + ")"

            rewritten = Equation.beautify(rewritten)
            return PointSlope(rewritten)

        if form == "Slope-Intercept":
            operator = "+" if self.y_intercept > 0 else ""
            rewritten = "y=" + slope + "x" + operator + str(self.y_intercept)

            rewritten = Equation.beautify(rewritten)
            return SlopeIntercept(rewritten)

        return None


class PointSlope(Linear):
    """Class for all linear equations of Point-Slope form."""

    def __init__(self, equation):
        Linear.__init__(self, equation)

    def __str__(self):
        return self.equation

    def sort_for_x(self):
        """Sorts equation for x."""

        eqtn, y_index = self.equation, self.equation.index('y')
        x_index = eqtn.index('x')
        y_point = self.get_number(eqtn[y_index + 2], y_index + 2, eqtn)
        x_point = self.get_number(eqtn[x_index + 2], x_index + 2, eqtn)

        slope_pos = self.equal_index + 1

        # Gets the slope instead of using self.slope because this method is called
        # before defining (and to define) the slope attribute.

        slope = self.get_number(eqtn[slope_pos], slope_pos, eqtn)

        first_op = if_assign(eqtn[y_index + 1] == '-', '+', '-')
        second_op = eqtn[x_index + 1]

        sol_side = slope + "*(x" + second_op + x_point + ")" + first_op + y_point
        sol_side = Equation.beautify(sol_side)

        return sol_side

    def sort_for_y(self):
        """Sorts equation for y."""

        # Required and convenient variables definition.
        eqtn, y_index = self.equation, self.equation.index('y')
        x_index = eqtn.index('x')
        y_point = self.get_number(eqtn[y_index + 2], y_index + 2, eqtn)
        x_point = self.get_number(eqtn[x_index + 2], x_index + 2, eqtn)
        x_point_op = if_assign(eqtn[x_index + 1] == '-', '-', '+')

        # Expression
        sol_side = "(y" + eqtn[y_index + 1] + y_point + "-" + str(self.slope) + \
                   "*" + x_point_op + x_point + ")/" + str(self.slope)

        sol_side = Equation.beautify(sol_side)
        return sol_side

    def sort(self, for_variable):
        """Sorts a Point-Slope Form linear equation
        to be solved for a given variable.

        Keyword arguments:

        variable (str): the variable this equation will be sorted to solve for."""

        if for_variable == 'y':
            return self.sort_for_y()
        if for_variable == 'x':
            return self.sort_for_x()
        return None

    def express_as(self, form):
        """Expresses the equation in the form passed as an argument
        and returns an instance of that form's class as the new expression.

        Valid forms are Slope-Intercept, Standard and Point-Slope.
        Keyword arguments:

        form (str): the form the equation will be converted to"""

        eqtn, slope = self.equation, str(self.slope)
        forms = ["Slope-Intercept", "Point-Slope", "Standard"]

        if form not in forms:
            raise InvalidFormError(form, forms)
        if form in self.form:
            raise RedundantConversionError(form)

        if form == 'Slope-Intercept':

            operator = if_assign(self.y_intercept < 0, '', '+')
            rewritten = 'y=' + slope + "x" + operator + str(self.y_intercept)

            if '--' in rewritten:
                rewritten = rewritten.replace('--', '+')

            return SlopeIntercept(rewritten)

        if form == 'Standard':
            operator = if_assign(eqtn[0] == '-', '-', '+')
            y_mult = if_assign(self.y_mult == '1', '', self.y_mult)

            rewritten = '-' + self.x_mult + 'x' + operator + \
                        y_mult + 'y' + '=' + str(self.y_intercept)

            rewritten = Equation.beautify(rewritten)

            return Standard(rewritten)

        return None


class LinearSystem:
    """This class defines the Linear System object to work with
    systems of equations."""

    def __init__(self, first_equation, second_equation):
        self.linear_1 = self.convert(first_equation)
        self.linear_2 = self.convert(second_equation)

    def is_compatible(self):
        """Returns true if there's any value of x that equally satisfies
        both equations."""

        if self.linear_1.slope != self.linear_2.slope:
            return True
        elif self.linear_2.y_intercept == self.linear_1.y_intercept:
            return True

        return False

    def get_number_of_solutions(self):
        """ Returns the number of solutions for this system
        of equations"""

        if self.is_compatible() is True:
            if self.linear_1.points(1, 2) == self.linear_2.points(1, 2):
                return 'Infinitely many solutions'

            return 'One solution'

        return 'No solutions'

    def convert(self, linear):
        """Converts a linear equation to Slope-Intercept form if under other form."""
        try:
            return linear.express_as('Slope-Intercept')
        except RedundantConversionError:
            return linear

    def solve(self):
        """Returns the solution to this system of equation."""

        if self.is_compatible() is False:
            return None
        if self.get_number_of_solutions() == 'Infinitely many solutions':
            raise InfinitelySolutionsError

        x_mult = str(num(self.linear_2.x_mult) - num(self.linear_1.x_mult))
        x_mult = '' if x_mult == '1' else x_mult
        equation = x_mult + 'x' + '=' + str(self.linear_1.y_intercept) + '-' + str(self.linear_2.y_intercept)

        x_value = Equation(equation).solve()

        return self.linear_1.get_point(x_value)

    def graph(self):

        solution_point = self.solve()
        x_solution, y_solution = solution_point[0], solution_point[1]

        first_line = self.linear_1.points(x_solution - 3, x_solution + 3) # ERROR : THIS TAKES POINTS SINCE X = X_SOLUTION TILL X!!! = Y SOLUTION?)?
        second_line = self.linear_2.points(x_solution - 3, x_solution + 3) # ERROR

        first_x, first_y, second_x, second_y = [], [], [], []

        first_x.extend((first_line[0][0], first_line[-1][0]))
        first_y.extend((first_line[0][1], first_line[-1][1]))

        second_x.extend((second_line[0][0], second_line[-1][0]))
        second_y.extend((second_line[0][1], second_line[-1][1]))

        plt.plot(first_x, first_y)
        plt.plot(second_x, second_y)

        plt.plot([3, 3], [0, y_solution], 'r--')
        plt.plot([0, x_solution], [y_solution, y_solution], 'r--')

        plt.ylabel("Y = " + str(y_solution))
        plt.xlabel("X = " + str(x_solution))

        plt.show()

    compatible = property(is_compatible)
    solutions = property(get_number_of_solutions)


