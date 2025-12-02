# 🧪 QuimikeyLab App

### Interface em Python para o sistema interativo de elementos químicos

O **QuimikeyLab** é uma aplicação desktop desenvolvida em **Python**, criada para complementar o sistema físico **Quimikey**, exibindo no computador informações detalhadas sobre elementos químicos em tempo real.  
O software foi projetado para uso em **laboratórios educacionais, feiras de ciências, e projetos maker acessíveis**, permitindo interação tanto via **teclado matricial** quanto **joystick analógico** conectados ao microcontrolador.

---

## 🧠 Visão Geral

O aplicativo recebe dados do Arduino via **porta serial** no formato **JSON**, exibindo:

- 🧷 Nome e símbolo do elemento;
- 🔢 Número atômico e massa atômica;
- 🌈 Família química (com cores associadas);
- ⚡ Animações visuais e feedbacks interativos;
- 🧍‍♂️ Recursos de acessibilidade (modo alto contraste e narração opcional).

Além disso, a versão mais recente do **QuimikeyLab** inclui:

- 🔄 **Suporte a Docker**, facilitando o deployment e a execução do aplicativo em qualquer sistema.
- 🔧 **Exibição 3D dos elementos**, permitindo visualização interativa e detalhada de cada elemento químico.

O **QuimikeyLab** foi projetado com uma arquitetura modular, permitindo expansão para novas interfaces, sensores ou modos de visualização (como gráficos de propriedades químicas).

---

## 👥 Autores e Colaboradores

- 👨‍🔬 **José Ubirajara Moreira Tavares** — Técnico em Eletrônica, desenvolvedor principal do hardware e firmware Arduino.  
- 👨‍💻 **Jeferson Schneider** — Desenvolvedor Python e colaborador responsável pela integração PC-App e design da interface gráfica.  

---

## ⚙️ Tecnologias Utilizadas

- **Python 3.10+**
- **PySerial** — Comunicação serial com Arduino  
- **Tkinter / PyQt5** — Interface gráfica (GUI)  
- **JSON** — Formato de troca de dados  
- **Threading** — Para leitura assíncrona da serial  
- **Matplotlib (opcional)** — Visualização de propriedades químicas  
- **Docker** — Containerização para facilitar o deploy e a execução multiplataforma  
- **PyOpenGL / VTK** — Para renderização 3D dos elementos químicos

---

## 🧩 Estrutura do Projeto

