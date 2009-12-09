class Button {
  float x1,y1, x2,y2;

  Button (float _x1, float _y1, float _x2, float _y2) {
    x1 = _x1;
    y1 = _y1;
    x2 = _x2;
    y2 = _y2;
  }

  void draw() {
    rect(x1,y1, x2-x1,y2-y1);
  }

  void click() {
    println("Click!");
  }
}

class ButtonMatrix {
  ArrayList buttons;

  float base_x = 0;
  float base_y = 0;

  float max_x = 0;
  float max_y = 0;

  float step_x = 0;
  float step_y = 0;

  ButtonMatrix (float width, float height, float x_step, float y_step) {
    buttons = new ArrayList();

    max_x = width;
    max_y = height;

    step_x = x_step; // XXX eww?
    step_y = y_step;

    int rows = (int)height/(int)y_step;
    int cols = (int)width/(int)x_step;
  
    for(int r = 0; r < rows; r++) {
      ArrayList cur_row = new ArrayList();
      for(int c = 0; c < cols; c++) {
        Button b = new Button(r*x_step, c*y_step, (r+1)*x_step, (c+1)*y_step);
        cur_row.add(b);
      }
      buttons.add(cur_row);
    }
  }

  void draw() {
    for(int r = 0; r < buttons.size(); r++) {
      ArrayList cur_row = (ArrayList) buttons.get(r);
      for(int c = 0; c < cur_row.size(); c++) {
        Button b = (Button) cur_row.get(c);
        b.draw();
      }
    }
  }

  void click(float x, float y) {
    int r = (int)(x - base_x) / (int)step_x;
    int c = (int)(y - base_y) / (int)step_y;

    Button b = (Button)( (ArrayList)buttons.get(r)).get(c);

    b.click();
    
  }
}


ButtonMatrix buttonMatrix;

void setup() {
  size(400, 450);
  smooth();

  background(255);

  buttonMatrix = new ButtonMatrix(400, 450, 50, 50);

}


void draw() {
  buttonMatrix.draw();
}

void mouseReleased() {
  buttonMatrix.click(mouseX, mouseY); // magic constants yay!
}
