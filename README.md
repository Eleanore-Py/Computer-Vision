## 📐 Mathematical Explanation of Eye Aspect Ratio (EAR)

### What is EAR?

Eye Aspect Ratio (EAR) is a geometric-based metric used to measure eye openness by analyzing the relative distances between specific eye landmarks. It is widely used in eye blink detection systems because it is **simple, efficient, and invariant to scale**.

EAR works under a simple observation:

* When the eye is **open**, the vertical distances between eyelids are relatively large.
* When the eye is **closed**, these vertical distances shrink toward zero, while the horizontal eye width remains almost constant.

---

### Eye Landmark Representation

Each eye is represented by **6 landmark points**:

```
P1 ---- P4
 |      |
P2      P6
 |      |
P3 ---- P5
```

Where:

* **P1 & P4** → horizontal eye corners
* **P2, P3, P5, P6** → upper and lower eyelid points

---

### EAR Formula

The Eye Aspect Ratio is defined as:

[
EAR = \frac{||P2 - P6|| + ||P3 - P5||}{2 \times ||P1 - P4||}
]

Where:

* ( ||P_i - P_j|| ) is the **Euclidean distance** between two landmark points

---

### Step-by-Step Breakdown

1. **Vertical distances (eye height):**

   * ( A = ||P2 - P6|| )
   * ( B = ||P3 - P5|| )

2. **Horizontal distance (eye width):**

   * ( C = ||P1 - P4|| )

3. **Compute EAR:**

   * ( EAR = (A + B) / (2C) )

---

### Blink Detection Logic

* EAR value remains **almost constant** when eyes are open
* EAR value **drops sharply** when eyes close

A blink is detected when:

* EAR falls **below a predefined threshold** for a certain number of consecutive frames

Typical values:

* EAR (open eye): `~0.25 – 0.30`
* EAR (closed eye): `< 0.20`

---

### Why EAR Works Well

✔ Scale-invariant (works regardless of face distance to camera)
✔ Computationally lightweight (real-time capable)
✔ Robust for both classical CV and ML-based landmark detectors

---

### Limitations

* Sensitive to inaccurate landmark detection
* Threshold may vary across individuals
* Extreme head rotations may affect accuracy

---

### Summary

The Eye Aspect Ratio transforms facial landmark geometry into a simple numerical signal that reliably represents eye state (open or closed). By combining EAR with temporal logic, real-time and accurate eye blink detection can be achieved.

This makes EAR a practical bridge between **machine learning-based landmark detection** and **rule-based computer vision logic**.
