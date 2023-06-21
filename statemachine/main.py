class StateA():
    """ 状態A """
    def __init__(self):
        # StateAに遷移した時に実行されるアクション
        print("State A")

    def on_event(self, event):
        # イベントを受け取った時に実行されるアクションと状態遷移
        if event == "1":
            # イベントが1の時にStateBに遷移する
            print("--(1)--> State B")
            return StateB()
        elif event == "2":
            # イベントが2の時にStateCに遷移する
            print("--(2)--> State C")
            return StateC()
        
        print("イベントに対応する遷移条件なし")
        return self


class StateB():
    """ 状態B """
    def __init__(self):
        # StateBに遷移した時に実行されるアクション
        print("State B")

    def on_event(self, event):
        # イベントを受け取った時に実行されるアクションと状態遷移
        if event == "2":
            # イベントが2の時にStateAに遷移する
            print("--(2)--> State B")
            return StateA()
        
        print("イベントに対応する遷移条件なし")
        return self


class StateC():
    """ 状態C """
    def __init__(self):
        # StateCに遷移した時に実行されるアクション
        print("State C")

    def on_event(self, event):
        # イベントを受け取った時に実行されるアクションと状態遷移
        if event == "1":
            # イベントが1の時にStateAに遷移する
            print("--(1)--> State A")
            return StateA()
        
        print("イベントに対応する遷移条件なし")
        return self


class StateMachine:
    """ 状態遷移を管理する状態遷移マシン """
    def __init__(self):
        # 状態Aを初期状態とする
        self.current_state = StateA()

    def transition(self, event):
        # イベントに応じて状態を遷移させる
        # 遷移に関係ないイベントを受け取った場合、状態は遷移せずアクションも実行しない
        self.current_state = self.current_state.on_event(event)


# =======================
# ここから使用例
# =======================
machine = StateMachine() # 初期状態 State A

while True:
    event = input('数値を入力してください ')
    machine.transition(event)
